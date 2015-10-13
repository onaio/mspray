from django.contrib.gis.db import models


class SprayPoint(models.Model):
    data_id = models.CharField(max_length=50)
    sprayday = models.ForeignKey('SprayDay')
    location = models.ForeignKey('Location')

    class Meta:
        app_label = 'main'
        unique_together = (('data_id', 'location'))

    def __str__(self):
        return self.data_id
