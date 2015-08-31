# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20150825_1113'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=1, max_length=255)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
                ('code', models.CharField(db_index=1, max_length=10)),
                ('level', models.CharField(db_index=1, max_length=50)),
                ('parent', models.ForeignKey(null=True, to='main.Location')),
            ],
        ),
    ]
