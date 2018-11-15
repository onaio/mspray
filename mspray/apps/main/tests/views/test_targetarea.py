"""Test mobilisation module."""
from django.test import RequestFactory, TestCase

from mspray.apps.main.models import Location
from mspray.apps.main.tests.utils import data_setup


from mspray.apps.main.views.home import TargetAreaView


class TestTargetAreaView(TestCase):
    """Test mobilisation view."""

    def test_mobilisation(self):
        """Test processing a mobilisation visit via MobilisationView."""
        data_setup()
        sprayarea = Location.objects.get(name='Akros_1')
        factory = RequestFactory()
        view = TargetAreaView.as_view()

        # Test mobilizatiion has not been mobilised
        request = factory.get("/2/3")
        response = view(
            request,
            district_pk=sprayarea.parent_id, slug=sprayarea.id)
        self.assertContains(
            response,
            'Mobilised? \
            <i class="fa fa-times" style="color: red"></i>',
            html=True)

        # mobilize the location
        sprayarea.is_mobilised = True
        sprayarea.save()

        # Test the location is mobilised
        response = view(
            request, district_pk=sprayarea.parent_id,
            slug=sprayarea.id)
        self.assertContains(
            response,
            'Mobilised? \
            <i class="fa fa-check-circle" style="color: green"></i>',
            html=True)

    def test_sensitization(self):
        """Test processing a sensitiza visit via MobilisationView."""
        data_setup()
        factory = RequestFactory()
        sprayarea = Location.objects.get(name='Akros_1')
        view = TargetAreaView.as_view()

        request = factory.get("/2/3")
        response = view(
            request,
            district_pk=sprayarea.parent_id, slug=sprayarea.id)
        self.assertContains(
            response,
            'Mobilised? <i class="fa fa-times" style="color: red"></i>',
            html=True)

        sprayarea.is_sensitized = True
        sprayarea.save()

        response = view(
            request, district_pk=sprayarea.parent_id,
            slug=sprayarea.id)

        self.assertContains(
            response,
            'Community Ready? \
            <i class="fa fa-check-circle" style="color: green"></i>',
            html=True)
