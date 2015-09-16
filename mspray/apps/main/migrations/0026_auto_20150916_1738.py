# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_household_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sprayday',
            name='location',
            field=models.ForeignKey(null=True, to='main.Location'),
        ),
    ]
