from django.conf.urls import url

from mspray.apps.alerts.views import start_health_facility_catchment


urlpatterns = [
    url(r'^health-facility-catchment/$', start_health_facility_catchment,
        name='health_facility_catchment')
]
