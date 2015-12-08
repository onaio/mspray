# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0038_spraypointview'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hhcsv',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('osmid', models.IntegerField()),
                ('y', models.FloatField()),
                ('x3', models.FloatField()),
                ('shape_area', models.FloatField()),
                ('shape_length', models.FloatField()),
            ],
            options={
                'db_table': 'households',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OsmData',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('osmid', models.IntegerField()),
                ('target_area', models.CharField(max_length=100)),
                ('district', models.CharField(max_length=20)),
                ('building', models.CharField(max_length=3)),
                ('shape_area', models.FloatField()),
                ('shape_length', models.FloatField()),
            ],
            options={
                'db_table': 'osm_data',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MatchedData',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('osmid', models.IntegerField()),
                ('target_area', models.CharField(max_length=100)),
                ('district', models.CharField(max_length=20)),
                ('building', models.CharField(max_length=3)),
                ('shape_area', models.FloatField()),
                ('shape_length', models.FloatField()),
                ('y', models.FloatField()),
                ('x3', models.FloatField()),
            ],
        ),
    ]
