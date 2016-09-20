# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-09-20 08:48
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20160920_0739'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='way',
            name='nd_path',
        ),
        migrations.AddField(
            model_name='way',
            name='geom',
            field=django.contrib.gis.db.models.fields.PolygonField(null=True, srid=4326),
        ),
    ]
