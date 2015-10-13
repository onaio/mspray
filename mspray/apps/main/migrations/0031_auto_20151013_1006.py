# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_auto_20151009_0736'),
    ]

    operations = [
        migrations.AddField(
            model_name='sprayday',
            name='spray_operator',
            field=models.ForeignKey(to='main.SprayOperator', null=True),
        ),
        migrations.AddField(
            model_name='sprayday',
            name='team_leader',
            field=models.ForeignKey(to='main.TeamLeader', null=True),
        ),
        migrations.AlterField(
            model_name='sprayday',
            name='bgeom',
            field=django.contrib.gis.db.models.fields.GeometryField(srid=4326, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='sprayday',
            name='geom',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, db_index=True, null=True),
        ),
    ]
