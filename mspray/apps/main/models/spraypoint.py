from django.contrib.gis.db import models


class SprayPoint(models.Model):
    data_id = models.CharField(max_length=50, unique=True)
    sprayday = models.ForeignKey('SprayDay')

    class Meta:
        app_label = 'main'

    def __str__(self):
        return self.data_id
