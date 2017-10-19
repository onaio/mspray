import codecs
import csv
import gc
import os

from django.core.management.base import BaseCommand
# from django.db.models import Count
from django.db.models import Q
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location
from mspray.apps.main.models import SprayDay


def spray_area_calculations(loc, stdout_write=print):
    qs = SprayDay.objects.filter(location=loc)
    total_submissions = qs.count()
    stdout_write(total_submissions, "Total Submissions")
    unsprayable = qs.filter(
        was_sprayed=False, data__contains={'sprayable_structure': 'no'}
    ).count()

    sprayable = qs.filter(
        data__contains={'sprayable_structure': 'yes'}
    )
    stdout_write(unsprayable, "Total Unsprayable")

    sprayed = qs.filter(was_sprayed=True).count()
    stdout_write(sprayed, "Total Sprayed")

    not_sprayed = qs.filter(
        was_sprayed=False, data__contains={'sprayable_structure': 'yes'}
    ).count()
    stdout_write(not_sprayed, "Total Not Sprayed")

    not_sprayed_wo = qs.filter(
        was_sprayed=False, data__contains={'sprayable_structure': 'yes'},
        spraypoint__isnull=False
    ).count()
    stdout_write(not_sprayed_wo, "Not Sprayed (without duplicates)")

    new_structures = sprayable.filter(
        Q(data__has_key='osmstructure:node:id') |
        Q(data__has_key='newstructure/gps')
    ).count()
    stdout_write(new_structures,
                 "Total New structures(not sprayable not included)")

    osmids = qs.filter(
        was_sprayed=True, data__contains={'sprayable_structure': 'yes'}
    ).values('osmid').distinct()
    osmids_count = osmids.count()
    stdout_write(
        osmids_count,
        "Total distinct structures sprayed on %s (no duplicates)" % loc
    )

    not_sprayable_before = SprayDay.objects.filter(
        location=loc,
        data__contains={'sprayable_structure': 'no'},
        osmid__in=osmids
    ).values('osmid').count()
    stdout_write(
        not_sprayable_before,
        "structures that had 'not sprayable' status on %s" % loc)

    not_sprayed_before = SprayDay.objects.filter(
        location=loc, was_sprayed=False,
        osmid__in=osmids
    ).values('osmid').count()
    stdout_write(
        not_sprayed_before,
        "structures that had 'not sprayed' on %s" % loc)

    structures = loc.structures
    stdout_write(structures, "enumerated structures")

    return (loc, total_submissions, unsprayable, sprayed, not_sprayed,
            not_sprayed_wo, osmids_count, new_structures, not_sprayed_before,
            not_sprayable_before, structures)


def spray_date_calculations(locs, spray_date, stdout_write=print):
    qs = SprayDay.objects.filter(location__name__in=locs,
                                 spray_date=spray_date)
    total_submissions = qs.count()
    stdout_write(total_submissions, "Total Submissions")
    unsprayable = qs.filter(
        was_sprayed=False, data__contains={'sprayable_structure': 'no'}
    ).count()
    sprayable = qs.filter(
        data__contains={'sprayable_structure': 'yes'}
    )
    stdout_write(unsprayable, "Total Non-eligible")
    sprayed = qs.filter(was_sprayed=True).count()
    stdout_write(sprayed, "Total Sprayed")
    not_sprayed = qs.filter(
        was_sprayed=False, data__contains={'sprayable_structure': 'yes'}
    ).count()
    stdout_write(not_sprayed, "Total Not Sprayed")
    new_structures = sprayable.filter(
        Q(data__has_key='osmstructure:node:id') |
        Q(data__has_key='newstructure/gps')
    ).count()
    stdout_write(new_structures,
                 "Total New structures(not eligible not included)")
    osmids = qs.filter(
        was_sprayed=True, data__contains={'sprayable_structure': 'yes'}
    ).values('osmid').distinct()
    osmids_count = osmids.count()
    stdout_write(osmids_count,
                 "Total distinct structures sprayed on %s (no duplicates)"
                 % spray_date)
    not_sprayable_before = SprayDay.objects.filter(
        location__name__in=locs,
        data__contains={'sprayable_structure': 'no'},
        osmid__in=osmids, spray_date__lt=spray_date
    ).values('osmid').count()
    stdout_write(not_sprayable_before,
                 "structures that had 'not eligible' status before "
                 "%s (previous count)" % spray_date)
    not_sprayed_before = SprayDay.objects.filter(
        location__name__in=locs, was_sprayed=False,
        osmid__in=osmids, spray_date__lt=spray_date
    ).values('osmid').count()
    stdout_write(not_sprayed_before,
                 "structures that had 'not sprayed' status before "
                 "%s (previous count)" % spray_date)
    sprayed_before = SprayDay.objects.filter(
        location__name__in=locs, was_sprayed=True,
        osmid__in=osmids, spray_date__lt=spray_date
    ).values('osmid').count()
    stdout_write(sprayed_before,
                 "structures that had 'sprayed' status before "
                 "%s (previous count)" % spray_date)

    return (spray_date, total_submissions, unsprayable, sprayed, not_sprayed,
            osmids_count, new_structures, not_sprayed_before, sprayed_before,
            not_sprayable_before)


class Command(BaseCommand):
    help = _('Troubleshooting')

    def handle(self, *args, **options):
        def logwriter(*args):
            fmt = u""
            for arg in args:
                fmt += "%s "
            self.stdout.write(fmt % (args))

        stdout_write = logwriter
        location = Location.objects.get(pk=70)
        qs_all = SprayDay.objects.filter(location__parent__id=location.pk)
        # locs = list(qs_all.values_list('location__name', flat=True))
        stdout_write(qs_all.first().location.parent.name)
        # qs = qs_all.values('spray_date').distinct()\
        #     .annotate(submissions=Count('id'))\
        #     .order_by('spray_date')

        # qs = location.location_set.all().order_by('name')

        def do_calculations(qs):
            yield ("spray_area", "total_submissions", "unsprayable", "sprayed",
                   "not_sprayed", "not_sprayed_wo_duplicates",
                   "distinct_structures", "new_structures",
                   "not_sprayed_before", "not_sprayable_before",
                   "enumerated_structures")
            for i in qs:
                # spray_date = i.get('spray_date')
                # stdout_write(spray_date, i.get('submissions'))
                stdout_write(i.name)
                stdout_write('-------------------------------')
                # yield spray_date_calculations(locs, spray_date)
                yield spray_area_calculations(i, stdout_write)
                stdout_write('-------------------------------')
                stdout_write('-------------------------------')

        dir_path = '/tmp/troubleshooting'
        try:
            os.mkdir(dir_path)
        except:
            pass
        for rhc in Location.objects.filter(level='RHC'):
            qs = rhc.location_set.all().order_by('name')
            fn = os.path.join(dir_path,
                              '%s_%s.csv' % (rhc.parent.name, rhc.name))
            with codecs.open(fn, 'w', encoding='utf-8') as f:
                writer = csv.writer(f)
                for i in do_calculations(qs):
                    writer.writerow(i)
            gc.collect()
