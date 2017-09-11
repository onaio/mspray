from django.conf.urls import url

from mspray.apps.warehouse.views import LocationDetailView, TargetAreas

urlpatterns = [
    url(r'^spray-effectiveness/location/(?P<pk>\d+)/$',
        LocationDetailView.as_view(),
        name='rhc'),
    url(r'^spray-effectiveness/spray-areas/$', TargetAreas.as_view(),
        name='spray_areas'),
]
