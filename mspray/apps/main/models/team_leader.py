from django.contrib.gis.db import models


class TeamLeader(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, db_index=1)

    class Meta:
        app_label = 'main'

    def __str__(self):
        return '{}'.format(self.name)
