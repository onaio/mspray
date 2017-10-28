# -*- coding=utf-8 -*-
"""
Generate OSM file
"""
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location, SprayDay
from mspray.apps.main.ona import fetch_osm_xml_data
from mspray.apps.main.osm import _get_xml_obj, etree


class Command(BaseCommand):
    """
    Generate OSM file
    """
    help = _('Generate OSM file from HH data.')

    def handle(self, *args, **options):
        locations = Location.objects.filter(level='ta').order_by('pk')
        for location in locations:
            osm = None
            queryset = SprayDay.objects.filter(location=location)
            for submission in queryset:
                submission_osm = fetch_osm_xml_data(submission.data)
                if submission_osm:
                    submission_osm_obj = _get_xml_obj(submission_osm)
                    if submission_osm_obj is None:
                        continue
                    for way in submission_osm_obj.findall('way'):
                        # pylint: disable=no-member
                        way.append(etree.Element(
                            'tag', {'k': 'spray_date',
                                    'v': '%s' % submission.spray_date}))
                        way.append(etree.Element(
                            'tag', {'k': 'spray_area',
                                    'v': '%s' % submission.location.name}))
                        way.append(etree.Element(
                            'tag',
                            {'k': 'health_facility',
                             'v': '%s' % submission.location.parent.name}))
                        way.append(etree.Element(
                            'tag',
                            {'k': 'district',
                             'v':
                             '%s' % submission.location.parent.parent.name}))
                    if osm is None:
                        osm = submission_osm_obj
                        continue
                    for child in submission_osm_obj.getchildren():
                        osm.append(child)
            if osm is not None:
                # pylint: disable=no-member
                xml = etree.tostring(osm, encoding='utf-8',
                                     xml_declaration=True)
                osm_file = open('/home/ukanga/data/mspray/2016/osm/%s.osm.xml'
                                % location.name, 'wb')
                osm_file.write(xml)
                osm_file.close()
