from rest_framework.decorators import api_view
from rest_framework.response import Response

from mspray.apps.alerts.tasks import health_facility_catchment_hook


@api_view()
def start_health_facility_catchment(request):
    health_facility_catchment_hook.delay()
    return Response({"success": True})
