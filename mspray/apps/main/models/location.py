from django.contrib.gis.db import models


class Location(models.Model):
    name = models.CharField(max_length=255, db_index=1)
    level = models.CharField(db_index=1, max_length=50)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    code = models.PositiveIntegerField()
    rank = models.PositiveIntegerField()
    homesteads = models.PositiveIntegerField(default=0)
    structures = models.PositiveIntegerField(default=0)
    geom = models.MultiPolygonField(srid=4326, null=True)

    objects = models.GeoManager()

    class Meta:
        app_label = 'main'
        unique_together = ('code', 'rank', 'level', 'parent')

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
