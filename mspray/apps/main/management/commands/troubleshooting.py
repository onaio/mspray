import codecs
import csv
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db.models import Q
from django.utils.translation import gettext as _

from mspray.apps.main.models import SprayDay


def calculations(locs, spray_date):
    qs = SprayDay.objects.filter(location__name__in=locs,
                                 spray_date=spray_date)
    total_submissions = qs.count()
    print(total_submissions, "Total Submissions")
    unsprayable = qs.filter(
        was_sprayed=False, data__contains={'sprayable_structure': 'no'}
    ).count()
    sprayable = qs.filter(
        data__contains={'sprayable_structure': 'yes'}
    )
    print(unsprayable, "Total Unsprayable")
    sprayed = qs.filter(was_sprayed=True).count()
    print(sprayed, "Total Sprayed")
    not_sprayed = qs.filter(
        was_sprayed=False, data__contains={'sprayable_structure': 'yes'}
    ).count()
    print(not_sprayed, "Not Sprayed")
    new_structures = sprayable.filter(
        Q(data__has_key='osmstructure:node:id') |
        Q(data__has_key='newstructure/gps')
    ).count()
    print(new_structures, "Total New structures(not sprayable not included)")
    osmids = qs.filter(
        was_sprayed=True, data__contains={'sprayable_structure': 'yes'}
    ).values('osmid').distinct()
    osmids_count = osmids.count()
    print(osmids_count,
          "Total distinct structures sprayed on %s (no duplicates)"
          % spray_date)
    not_sprayed_before = SprayDay.objects.filter(
        location__name__in=locs, was_sprayed=False,
        osmid__in=osmids, spray_date__lt=spray_date
    ).values('osmid').count()
    print(not_sprayed_before,
          "structures that had 'not sprayed' status before "
          "%s (previous count)" % spray_date)
    sprayed_before = SprayDay.objects.filter(
        location__name__in=locs, was_sprayed=True,
        osmid__in=osmids, spray_date__lt=spray_date
    ).values('osmid').count()
    print(sprayed_before,
          "structures that had 'sprayed' status before "
          "%s (previous count)" % spray_date)

    return (spray_date, total_submissions, unsprayable, sprayed, not_sprayed,
            osmids_count, new_structures, not_sprayed_before, sprayed_before)


class Command(BaseCommand):
    help = _('Troubleshooting')

    def handle(self, *args, **options):
        qs_all = SprayDay.objects.filter(location__parent__id=70)
        locs = list(qs_all.values_list('location__name', flat=True))
        print(qs_all.first().location.parent)
        qs = qs_all.values('spray_date').distinct()\
            .annotate(submissions=Count('id'))\
            .order_by('spray_date')

        def do_calculations():
            yield ("spray_date", "total_submissions", "unsprayable", "sprayed",
                   "not_sprayed", "distinct_structures", "new_structures",
                   "not_sprayed_before", "sprayed_before")
            for i in qs:
                spray_date = i.get('spray_date')
                print(spray_date, i.get('submissions'))
                print('-------------------------------')
                yield calculations(locs, spray_date)
                print('-------------------------------')
                print('-------------------------------')

        with codecs.open('/tmp/calculations.csv', 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            for i in do_calculations():
                writer.writerow(i)
