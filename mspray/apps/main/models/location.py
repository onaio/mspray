from django.contrib.gis.db import models


class Location(models.Model):
    name = models.CharField(max_length=255, db_index=1)
    code = models.CharField(max_length=10, db_index=1)
    level = models.CharField(db_index=1, max_length=50)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    structures = models.PositiveIntegerField(default=0)
    geom = models.MultiPolygonField(srid=4326, null=True)

    objects = models.GeoManager()

    class Meta:
        app_label = 'main'

    def __str__(self):
        return self.name
