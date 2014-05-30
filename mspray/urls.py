from django.conf.urls import patterns, include, url
from rest_framework import routers
from django.contrib import admin
admin.autodiscover()

from mspray.apps.main.views import target_area, household, sprayday, indicators

router = routers.DefaultRouter(trailing_slash=False)

router.register(r'targetareas', target_area.TargetAreaViewSet)
router.register(r'households', household.HouseholdViewSet)
router.register(r'spraydays', sprayday.SprayDayViewSet)

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'mspray.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', include(router.urls)),
    url(r'indicators/number_of_households',
        indicators.NumberOfHouseholdsIndicatorView.as_view(),
        name='number_of_housesholds'),
    url(r'^admin/', include(admin.site.urls)),
)
