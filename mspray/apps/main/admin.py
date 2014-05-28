from django.contrib.gis import admin
from mspray.apps.main.models.target_area import TargetArea

admin.site.register(TargetArea, admin.GeoModelAdmin)
