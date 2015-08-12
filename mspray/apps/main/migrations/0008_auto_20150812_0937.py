# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20150810_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='household',
            name='geom',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326),
        ),
    ]
