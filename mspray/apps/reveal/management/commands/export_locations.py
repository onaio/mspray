"""Django command to export locations to OpenSRP"""
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location
from mspray.apps.reveal.export.locations import (export_households,
                                                 export_locations,
                                                 export_rhc_target_areas)


class Command(BaseCommand):
    """
    Export locations
    """
    help = _("Export locations to OpenSRP one district at a time")

    def _districts(self):
        """
        Get the districts available and output them to stdout
        """
        districts = Location.objects.filter(level='district', target=True)
        if districts:
            self.stdout.write(_('Available Districts:'))
            for district in districts:
                self.stdout.write(f'{district.id} {district.name}')
        else:
            self.stderr.write(_('No Districts!'))

    def add_arguments(self, parser):
        """Command arguments"""
        parser.add_argument(
            'district_id',
            type=int,
            help=_('The district_id.'),
        )

    # pylint: disable=too-many-nested-blocks
    def handle(self, *args, **options):
        """
        Actually do the work!
        """
        try:
            field = options['district_id']
        except KeyError:
            raise CommandError(_('Please specify field to use.'))
        else:
            district_id = int(field)
            # get the queryset for this one district
            district_qs = Location.objects.filter(id=district_id, target=True)

            # if no district we cannot continue
            if district_qs:
                self.stdout.write(
                    f'Exporting district {district_qs.first().name}')
                # attempt to export the district
                district_res = export_locations(district_qs)

                if district_res:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Success - district: {district_qs.first().name}'))

                    # get the RHC objects
                    rhc_qs = Location.objects.filter(
                        parent__id=district_id, target=True)

                    # attempt to export the RHCs in this district
                    self.stdout.write(
                        f'Exporting RHCs in {district_qs.first().name}')
                    rhc_res = export_locations(rhc_qs)

                    if rhc_res:
                        self.stdout.write(self.style.SUCCESS(
                            f'Success - RHCs in {district_qs.first().name}'))

                        # loop through the RHC objects
                        for rhc in rhc_qs.iterator():
                            # attempt to export the target areas in RHC
                            self.stdout.write(
                                f'Exporting target areas in {rhc.name}')
                            ta_res = export_rhc_target_areas(rhc_id=rhc.id)

                            if ta_res:
                                self.stdout.write(self.style.SUCCESS(
                                    f'Success - target areas in {rhc.name}'))

                                # get the target areas
                                ta_qs = Location.objects.filter(
                                    parent=rhc, target=True)

                                # loop through target areas to export
                                # the structures
                                for ta in ta_qs.iterator():
                                    # attempt to export the structures in TA
                                    self.stdout.write(
                                        f'Exporting structures in {ta.name}')
                                    hh_res = export_households(location=ta)

                                    if hh_res:
                                        self.stdout.write(self.style.SUCCESS(
                                            'Success - structures in '
                                            f'{ta.name}'
                                        ))
                                    else:
                                        self.stderr.write(
                                            'Error: structures in '
                                            f'{ta.name} not exported')
                            else:
                                self.stderr.write(
                                    f'Error: target areas in {rhc.name} '
                                    'not exported')

                    else:
                        self.stderr.write(
                            f'Error: RHCs in {district_qs.first().name} '
                            'not exported')

                else:
                    self.stderr.write(
                        f'Error: district {district_qs.first().name} '
                        'not exported')
            else:
                # not valid district
                self.stderr.write(
                    f'Error: {district_id} is not a valid district id')
                self._districts()
