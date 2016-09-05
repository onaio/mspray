# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0042_auto_20151208_0758'),
    ]

    operations = [
        migrations.CreateModel(
            name='DirectlyObservedSprayingForm',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('correct_removal', models.CharField(max_length=5)),
                ('correct_mix', models.CharField(max_length=5)),
                ('rinse', models.CharField(max_length=5)),
                ('PPE', models.CharField(max_length=5)),
                ('CFV', models.CharField(max_length=5)),
                ('correct_covering', models.CharField(max_length=5)),
                ('leak_free', models.CharField(max_length=5)),
                ('correct_distance', models.CharField(max_length=5)),
                ('correct_speed', models.CharField(max_length=5)),
                ('correct_overlap', models.CharField(max_length=5)),
                ('district', models.CharField(max_length=10)),
                ('health_facility', models.CharField(max_length=50)),
                ('supervisor_name', models.CharField(max_length=10)),
                ('sprayop_code_name', models.CharField(max_length=10)),
                ('tl_code_name', models.CharField(max_length=10)),
                ('data', django_pgjson.fields.JsonField(default={})),
                ('spray_date', models.CharField(max_length=10)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SprayOperatorDailySummary',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('spray_form_id', models.CharField(max_length=10)),
                ('sprayed', models.IntegerField()),
                ('found', models.IntegerField()),
                ('sprayoperator_code', models.CharField(max_length=10)),
                ('data', django_pgjson.fields.JsonField(default={})),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
