"""views module for reveal"""
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from mspray.apps.reveal.utils import add_spray_data


@api_view(["GET", "POST"])
def add_spray_data_view(request):
    """Accepts data and passes it to the add_spray_data function"""
    if request.method == "POST":
        data = request.data
        try:
            add_spray_data(data)
        except ValidationError:
            pass
        else:
            return Response({"success": True}, status=status.HTTP_200_OK)

    return Response({"success": False}, status=status.HTTP_400_BAD_REQUEST)
