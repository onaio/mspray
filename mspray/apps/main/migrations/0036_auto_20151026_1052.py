# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_spraypointview'),
    ]

    operations = [
        migrations.CreateModel(
            name='SprayPointView',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('sprayable_structure', models.CharField(max_length=10)),
                ('unsprayed_reason', models.CharField(max_length=50)),
                ('location_code', models.CharField(max_length=50)),
                ('district_code', models.CharField(max_length=50)),
                ('team_leader_id', models.IntegerField()),
                ('team_leader_code', models.CharField(max_length=50)),
                ('team_leader_name', models.CharField(max_length=255)),
                ('spray_operator_id', models.IntegerField()),
                ('sprayoperator_code', models.CharField(max_length=10)),
                ('spray_date', models.DateField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'main_spray_point_view',
                'managed': False,
            },
        ),
        migrations.AddField(
            model_name='teamleader',
            name='location',
            field=models.ForeignKey(null=True, to='main.Location'),
        ),
    ]
