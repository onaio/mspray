from django.conf.urls import patterns, include, url
from rest_framework import routers
from django.contrib import admin
admin.autodiscover()

from mspray.apps.main.views import target_area, household

router = routers.DefaultRouter(trailing_slash=False)

router.register(r'targetareas', target_area.TargetAreaViewSet)
router.register(r'households', household.HouseholdViewSet)

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'mspray.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
)
