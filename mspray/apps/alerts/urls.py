from django.conf.urls import url

from mspray.apps.alerts.views import start_health_facility_catchment
from mspray.apps.alerts.views import start_so_daily_form_completion
from mspray.apps.alerts.views import start_send_weekly_update_email

urlpatterns = [
    url(r'^health-facility-catchment/$', start_health_facility_catchment,
        name='health_facility_catchment'),
    url(r'^so-daily-form-completion/$', start_so_daily_form_completion,
        name='so_daily_form_completion'),
    url(r'^weekly-update-email/$', start_send_weekly_update_email,
        name='send_weekly_update_email'),
]
