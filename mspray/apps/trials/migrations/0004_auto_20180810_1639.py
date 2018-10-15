# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-08-10 16:39
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trials', '0003_sample_bgeom'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sample',
            name='bgeom',
        ),
        migrations.AddField(
            model_name='sample',
            name='geom',
            field=django.contrib.gis.db.models.fields.GeometryField(db_index=True, null=True, srid=4326),
        ),
    ]