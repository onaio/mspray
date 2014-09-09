# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Household',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('hh_id', models.IntegerField()),
                ('hh_type', models.CharField(max_length=1)),
                ('comment', models.CharField(max_length=60)),
                ('type_1', models.CharField(max_length=1)),
                ('comment_1', models.CharField(max_length=60)),
                ('name', models.CharField(max_length=254)),
                ('descr', models.CharField(max_length=254)),
                ('orig_fid', models.IntegerField()),
                ('geom', django.contrib.gis.db.models.fields.MultiPointField(srid=4326)),
                ('bgeom', django.contrib.gis.db.models.fields.PolygonField(null=True, blank=True, srid=4326)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HouseholdsBuffer',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('num_households', models.IntegerField(default=0)),
                ('geom', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SprayDay',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('submission_id', models.PositiveIntegerField(unique=True)),
                ('spray_date', models.DateField(db_index=True)),
                ('geom', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('data', jsonfield.fields.JSONField(default={})),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TargetArea',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('targetid', models.FloatField(db_index=1)),
                ('predicted', models.FloatField(db_index=1)),
                ('predinc', models.FloatField(db_index=1)),
                ('ranks', models.FloatField(db_index=1)),
                ('houseranks', models.FloatField(db_index=1)),
                ('targeted', models.FloatField(db_index=1)),
                ('rank_house', models.CharField(max_length=50, db_index=1)),
                ('ranked_num', models.FloatField(db_index=1)),
                ('number_of', models.FloatField(db_index=1)),
                ('district_name', models.CharField(max_length=254)),
                ('houses', models.FloatField(db_index=1)),
                ('geom', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='householdsbuffer',
            name='target_area',
            field=models.ForeignKey(to='main.TargetArea'),
            preserve_default=True,
        ),
    ]
