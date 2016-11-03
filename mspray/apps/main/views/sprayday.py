import gc
import csv

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.settings import api_settings

from mspray.apps.main.models import Location
from mspray.apps.main.models import SprayPoint
from mspray.apps.main.models.spray_day import DATA_ID_FIELD
from mspray.apps.main.models.spray_day import DATE_FIELD
from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.serializers.sprayday import SubmissionSerializer
from mspray.apps.main.serializers.sprayday import SprayDayGeoSerializer
from mspray.apps.main.serializers.sprayday import SprayDayNamibiaSerializer
from mspray.apps.main.serializers.sprayday import SprayDayShapeSerializer
from mspray.apps.main.utils import add_spray_data
from mspray.apps.main.utils import delete_cached_target_area_keys
from mspray.apps.main.utils import queryset_iterator
from mspray.apps.main.utils import Echo
from mspray.libs.renderers import CSVRenderer


headers = [
    'district',
    'health_facility',
    'osmid',
    'spray_area',
    'submission_id',
    'was_sprayed',
    'data._duration',
    'data._edited',
    'data._id',
    'data._submission_time',
    'data._submitted_by',
    'data._uuid',
    'data._version',
    'data._xform_id_string',
    'data.deviceid',
    'data.district',
    'data.end',
    'data.formhub/uuid',
    'data.health_facility',
    'data.imei',
    'data.meta/instanceID',
    'data.meta/instanceName',
    'data.newstructure/gps',
    'data.newstructure/nostructure',
    'data.osmstructure',
    'data.osmstructure:building',
    'data.osmstructure:ctr:lat',
    'data.osmstructure:ctr:lon',
    'data.osmstructure:node:id',
    'data.osmstructure:source',
    'data.osmstructure:spray_status',
    'data.osmstructure:structure_type',
    'data.osmstructure:useraccuracy',
    'data.osmstructure:userlatlng',
    'data.osmstructure:way:id',
    'data.spray_area',
    'data.sprayable/irs_card_confirm',
    'data.sprayable/irs_card_num',
    'data.sprayable/sprayed/sprayed_childrenU5',
    'data.sprayable/sprayed/sprayed_females',
    'data.sprayable/sprayed/sprayed_males',
    'data.sprayable/sprayed/sprayed_nets',
    'data.sprayable/sprayed/sprayed_pregwomen',
    'data.sprayable/sprayed/sprayed_pregwomen_uNet',
    'data.sprayable/sprayed/sprayed_rooms',
    'data.sprayable/sprayed/sprayed_roomsfound',
    'data.sprayable/sprayed/sprayed_total_uNet',
    'data.sprayable/sprayed/sprayed_totalpop',
    'data.sprayable/sprayed/sprayed_u5_uNet',
    'data.sprayable/sprayop_code',
    'data.sprayable/sprayop_name',
    'data.sprayable/structure_head_name',
    'data.sprayable/unsprayed/population/unsprayed_children_u5',
    'data.sprayable/unsprayed/population/unsprayed_nets',
    'data.sprayable/unsprayed/population/unsprayed_pregnant_women',
    'data.sprayable/unsprayed/population/unsprayed_roomsfound',
    'data.sprayable/unsprayed/population/unsprayed_total_uNet',
    'data.sprayable/unsprayed/population/unsprayed_u5_uNet',
    'data.sprayable/unsprayed/reason',
    'data.sprayable/unsprayed/unsprayed_females',
    'data.sprayable/unsprayed/unsprayed_males',
    'data.sprayable/unsprayed/unsprayed_totalpop',
    'data.sprayable/was_sprayed',
    'data.sprayable_structure',
    'data.sprayformid',
    'data.start',
    'data.subscriberid',
    'data.supervisor_name',
    'data.tla_code',
    'data.tla_leader',
    'data.today',
]


def _data(qs):

        yield [elem for elem in headers]

        for i in queryset_iterator(qs):
            data = SubmissionSerializer(i).data
            row = []

            for h in headers:
                if h.startswith('data.'):
                    k, v = h.split('.')
                    val = data.get('data').get(v)
                else:
                    val = data.get(h)

                row.append(val)

            yield row


class SprayDayViewSet(viewsets.ModelViewSet):
    """
    List of households that have been sprayed.

    Query Parameters:
    - `day` - filter list of sprayed points for a specific day
    - `target_area` - filter spray points for a specific target
    - `ordering` - you can order by day field e.g `ordering=day` or \
    `ordering=-day`
    """
    queryset = SprayDay.objects.filter()
    serializer_class = SprayDayGeoSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('spray_date',)
    ordering_fields = ('spray_date',)
    ordering = ('spray_date',)
    renderer_classes = [CSVRenderer] + api_settings.DEFAULT_RENDERER_CLASSES

    def get_serializer_class(self):
        fmt = self.request.accepted_renderer.format
        if fmt == 'csv':
            return SubmissionSerializer

        if settings.OSM_SUBMISSIONS:
            return SprayDayShapeSerializer

        if settings.SITE_NAME == 'namibia':
            return SprayDayNamibiaSerializer

        return super(SprayDayViewSet, self).get_serializer_class()

    def filter_queryset(self, queryset):
        targetid = self.request.query_params.get('target_area')

        if targetid:
            target = get_object_or_404(Location, pk=targetid)
            if False:  # settings.MSPRAY_SPATIAL_QUERIES:
                queryset = queryset.filter(geom__coveredby=target.geom)
            else:
                if target.parent is None:
                    queryset = queryset.filter(location__parent=target)
                else:
                    queryset = queryset.filter(location=target)

        if getattr(settings, 'MSPRAY_UNIQUE_FIELD', None):
            queryset = queryset.filter(
                pk__in=SprayPoint.objects.values('sprayday')
            )

        queryset = queryset.select_related('location__parent__parent')

        return super(SprayDayViewSet, self).filter_queryset(queryset)

    def create(self, request, *args, **kwargs):
        has_id = request.data.get(DATA_ID_FIELD)
        spray_date = request.data.get(DATE_FIELD)

        if not has_id or not spray_date:
            data = {
                "error": _("Not a valid submission: _id - %s, date - %s"
                           % (has_id, spray_date))
            }
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            try:
                sprayday = add_spray_data(request.data)
            except ValidationError as e:
                data = {"error": "%s" % e}
                status_code = status.HTTP_400_BAD_REQUEST
            except IntegrityError as e:
                data = {"error": "%s" % e}
                status_code = status.HTTP_400_BAD_REQUEST
            else:
                data = {"success": _("Successfully imported submission with"
                                     " submission id %(submission_id)s."
                                     % {'submission_id': has_id})}
                status_code = status.HTTP_201_CREATED
                delete_cached_target_area_keys(sprayday)

        return Response(data, status=status_code)

    def list(self, request, *args, **kwargs):
        if request.query_params.get('dates_only') == 'true':
            self.object_list = self.filter_queryset(self.get_queryset())
            data = self.object_list\
                .values_list('spray_date', flat=True).distinct()

            return Response(data)

        if request.accepted_renderer.format == 'csv':
            self.object_list = self.filter_queryset(self.get_queryset())
            csv_buffer = Echo()
            writer = csv.writer(csv_buffer)
            response = StreamingHttpResponse(
                (writer.writerow(row) for row in _data(self.object_list)),
                content_type='text/csv'
            )
            response['Content-Disposition'] = \
                'attachment; filename="data_all.csv"'

            return response

        return super(SprayDayViewSet, self).list(request, *args, **kwargs)
