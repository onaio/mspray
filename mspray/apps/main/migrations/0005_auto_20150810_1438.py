# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_district_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='targetarea',
            name='houseranks',
        ),
        migrations.RemoveField(
            model_name='targetarea',
            name='number_of',
        ),
        migrations.RemoveField(
            model_name='targetarea',
            name='predicted',
        ),
        migrations.RemoveField(
            model_name='targetarea',
            name='predinc',
        ),
        migrations.RemoveField(
            model_name='targetarea',
            name='rank_house',
        ),
        migrations.RemoveField(
            model_name='targetarea',
            name='ranked_num',
        ),
        migrations.RemoveField(
            model_name='targetarea',
            name='ranks',
        ),
        migrations.AlterField(
            model_name='targetarea',
            name='targeted',
            field=models.IntegerField(default=1, db_index=1),
        ),
    ]
