from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _
from django.db.models import Count

from mspray.apps.main.models import Household
from mspray.apps.main.models import SprayDay
from mspray.apps.main.models import Location
from mspray.apps.main.tasks import add_unique_record


class Command(BaseCommand):
    """
    Remove Household duplicates.
    """
    help = _("Remove duplicate Household objects based on 'geom' field")

    allowed_fields = ['geom', 'bgeom']

    def add_arguments(self, parser):
        parser.add_argument('--field', dest='field', default='bgeom',
                            help='the field to use to get duplicates')

    def handle(self, *args, **options):
        try:
            field = options['field']
        except KeyError:
            raise CommandError(_('Please specify field to use'))
        else:
            if field not in self.allowed_fields:
                raise CommandError(_("Only 'geom' or 'bgeom' fields are "
                                     "supported at this time"))

        location_with_duplicates = Household.objects.filter().values(field)\
            .annotate(k=Count('id'))\
            .filter(k__gt=1)\
            .values_list('location', flat=True).distinct()
        for location_id in location_with_duplicates:
            hh_dupes = Household.objects.filter(location_id=location_id)\
                .values(field).annotate(k=Count('id')).filter(k__gt=1)

            total_deleted = 0
            total = hh_dupes.count()

            for household in hh_dupes:
                filter_kwargs = {field: household[field]}
                matching_hh = Household.objects.filter(**filter_kwargs)
                if matching_hh.count() > 1:
                    osmids = Household.objects.filter(**filter_kwargs)\
                        .values('hh_id')
                    submissions = SprayDay.objects.filter(osmid__in=osmids)\
                        .values_list('osmid', flat=True).order_by('spray_date')
                    number_submitted = submissions.count()
                    if number_submitted == 0:
                        total_deleted += matching_hh.exclude(
                            pk=matching_hh.first().pk).count()
                        matching_hh.exclude(pk=matching_hh.first().pk).delete()
                    else:
                        total_deleted += matching_hh.exclude(
                            hh_id=submissions.first()).count()
                        matching_hh.exclude(hh_id=submissions.first()).delete()
            location = Location.objects.get(pk=location_id)
            submissions = location.sprayday_set.filter(osmid__gt=0)\
                .exclude(osmid__in=location.household_set.values('hh_id'))

            for submission in submissions:
                submission.spraypoint_set.all().delete()
                add_unique_record(submission.pk, submission.location_id)

            location.structures = location.household_set.all().count()
            location.save()
            self.stdout.write("%s of %s household duplicates in %s have been "
                              "succussfully deleted." % (total_deleted, total,
                                                         location))
