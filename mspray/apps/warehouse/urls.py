from django.conf.urls import url

from mspray.apps.warehouse.views import RHCView, AllTargetAreas, Home,\
    DistrictView, TargetAreaMap, RHCMap, DistrictMap


urlpatterns = [
    url(r'^home/$', Home.as_view(), name='home'),
    url(r'^district/(?P<pk>\d+)/$', DistrictView.as_view(), name='district'),
    url(r'^rhc/(?P<pk>\d+)/$', RHCView.as_view(), name='rhc'),
    url(r'^target-area/map/(?P<pk>\d+)/$', TargetAreaMap.as_view(), name='ta'),
    url(r'^rhc/map/(?P<pk>\d+)/$', RHCMap.as_view(), name='rhc_map'),
    url(r'^district/map/(?P<pk>\d+)/$', DistrictMap.as_view(),
        name='district_map'),
    url(r'^spray-effectiveness/spray-areas/$', AllTargetAreas.as_view(),
        name='spray_areas'),
]
