# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20150813_0849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='targetarea',
            name='geom',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, null=True),
        ),
        migrations.AlterField(
            model_name='targetarea',
            name='targetid',
            field=models.IntegerField(db_index=1, unique=True),
        ),
    ]
