from django.contrib.gis.db import models


class TeamLeaderAssistant(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, db_index=1)
    location = models.ForeignKey('Location', null=True)
    data_quality_check = models.BooleanField(default=False)
    average_spray_quality_score = models.FloatField(default=0.0)
    team_leader = models.ForeignKey('TeamLeader', null=True)

    class Meta:
        app_label = 'main'

    def __str__(self):
        return '{}'.format(self.name)
