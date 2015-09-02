from mspray.apps.main.views import (
    target_area, household, household_buffer, sprayday, indicators, districts
)
from mspray.apps.main.views import home
from mspray.apps.main.views import performance

from django.conf import settings
from django.conf.urls import patterns, include, url, static
from rest_framework import routers
from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter(trailing_slash=False)

router.register(r'buffers', household_buffer.HouseholdBufferViewSet)
router.register(r'districts', districts.DistrictViewSet, 'district')
router.register(r'households', household.HouseholdViewSet)
router.register(r'spraydays', sprayday.SprayDayViewSet)
router.register(r'targetareas', target_area.TargetAreaViewSet)

performance_urls = [
    url(r'^$', performance.DistrictPerfomanceView.as_view(),
        name="districts"),
    url(r'^team-leaders/(?P<slug>[^/]+)',
        performance.TeamLeadersPerformanceView.as_view(),
        name="team-leaders"),
    url(r'^spray-operators/(?P<team_leader>[^/]+)/(?P<district_name>[^/]+)/summary',  # noqa
        'mspray.apps.main.views.performance.spray_operator_summary',
        name="spray-operator-summary"),
    url(r'^spray-operators/(?P<team_leader>[^/]+)/(?P<district_name>[^/]+)/(?P<spray_operator>[^/]+)/daily',  # noqa
        'mspray.apps.main.views.performance.spray_operator_daily',
        name="spray-operator-daily"),
    url(r'^definitions-and-conditions$',
        performance.DefinitionAndConditionView.as_view(),
        name='definitions-and-conditions'),
]

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'mspray.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^api/', include(router.urls)),
    url(r'^$', home.DistrictView.as_view(), name='index'),
    url(r'^(?P<district_name>\w+)$', home.DistrictView.as_view(),
        name='district'),
    url(r'^(?P<district_name>\w+)/(?P<slug>\w+)$',
        home.TargetAreaView.as_view(),
        name='target_area'),
    url(r'indicators/number_of_households',
        indicators.NumberOfHouseholdsIndicatorView.as_view(),
        name='number_of_housesholds'),
    url(r'^performance/', include(performance_urls, namespace='performance')),
    url(r'^admin/', include(admin.site.urls)),
) + static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
