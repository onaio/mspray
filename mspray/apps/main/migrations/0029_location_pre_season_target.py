# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-29 23:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_auto_20170905_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='pre_season_target',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
