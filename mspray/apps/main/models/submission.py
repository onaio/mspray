# This is an auto-generated Django model module created by ogrinspect.
from django.db import models
from jsonfield import JSONField


class Submission(models.Model):
    data = JSONField(default={})

    class Meta:
        app_label = 'main'
