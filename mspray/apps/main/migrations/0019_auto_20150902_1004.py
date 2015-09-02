# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20150902_0720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sprayoperator',
            name='code',
            field=models.CharField(unique=True, max_length=10),
        ),
    ]
