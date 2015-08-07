from django.contrib.gis.db import models


class District(models.Model):
    district_name = models.CharField(max_length=255, db_index=1)
    houses = models.IntegerField(db_index=1)
    geom = models.MultiPolygonField(srid=4326)
    code = models.CharField(max_length=10, db_index=1)

    objects = models.GeoManager()

    class Meta:
        app_label = 'main'

    def __str__(self):
        return self.district_name
