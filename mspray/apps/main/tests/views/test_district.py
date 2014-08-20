import os

from django.core.management import call_command
from django.shortcuts import urlresolvers
from django.test import TestCase, RequestFactory

from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.views.districts import DistrictViewSet


class TestDistrictViewSet(TestCase):
    def setUp(self):
        super(TestDistrictViewSet, self).setUp()

        fixtures_dir = os.path.join(
            os.path.dirname(__file__), '../', 'fixtures'
        )
        call_command('loaddata',
                     os.path.join(fixtures_dir, 'target_areas.json'))

        self.view = DistrictViewSet.as_view({
            'get': 'list'
        })
        self.factory = RequestFactory()

    def test_list(self):
        self.assertEqual(TargetArea.objects.count(), 12)
        self.assertEqual(TargetArea.objects.filter(
            targeted=TargetArea.TARGETED_VALUE).count(), 9)

        request = self.factory.get('/')
        response = self.view(request)
        self.assertEqual(len(response.data), 2)
        data = {'district_name': 'Mwansabombwe', 'num_target_areas': 8}
        self.assertIn(data, response.data)

    def test_targetareas_for_district(self):
        self.assertEqual(TargetArea.objects.count(), 12)
        data = {'district': 'Mwansabombwe'}

        request = self.factory.get('/', data)
        response = self.view(request)
        self.assertEqual(len(response.data), 8)

        data = {'targetid': '53_92', 'structures': 92}
        properties = [i for i in response.data[0].items()]

        for item in data.items():
            self.assertIn(item, properties)

    def test_link(self):
        try:
            urlresolvers.resolve('/districts')
        except:
            self.fail("Cannot resolve url /districts")
