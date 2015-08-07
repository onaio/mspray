# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('district_name', models.CharField(db_index=1, max_length=255)),
                ('houses', models.FloatField(db_index=1)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
        ),
    ]
