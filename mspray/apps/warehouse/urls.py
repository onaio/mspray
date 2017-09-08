from django.conf.urls import url

from mspray.apps.warehouse.views import LocationDetailView

urlpatterns = [
    url(r'^location/(?P<pk>\d+)/$', LocationDetailView.as_view(),
        name='location'),
]
