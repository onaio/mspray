from django.conf.urls import url

from mspray.apps.warehouse.views import RHCView, TargetAreas, Home,\
    DistrictView


urlpatterns = [
    url(r'^home/$', Home.as_view(), name='home'),
    url(r'^district/(?P<pk>\d+)/$', DistrictView.as_view(), name='district'),
    url(r'^rhc/(?P<pk>\d+)/$', RHCView.as_view(), name='rhc'),
    url(r'^spray-effectiveness/spray-areas/$', TargetAreas.as_view(),
        name='spray_areas'),
]
