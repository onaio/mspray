import os

from django.core.management import call_command
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
        self.assertEqual(TargetArea.objects.count(), 45)

        request = self.factory.get('/')
        response = self.view(request)
        self.assertEqual(len(response.data), 15)
        data = {'district_name': 'Chienge', 'num_target_areas': 3}
        self.assertIn(data, response.data)
