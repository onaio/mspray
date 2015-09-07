from django.contrib.gis.db import models


class Location(models.Model):
    name = models.CharField(max_length=255, db_index=1)
    code = models.CharField(max_length=50, db_index=1, unique=True)
    level = models.CharField(db_index=1, max_length=50)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    structures = models.PositiveIntegerField(default=0)
    geom = models.PolygonField(srid=4326, null=True)

    objects = models.GeoManager()

    class Meta:
        app_label = 'main'

    def __str__(self):
        return self.name

    @property
    def district_name(self):
        return self.name

    @property
    def targetid(self):
        return self.code

    @property
    def houses(self):
        return self.structures
