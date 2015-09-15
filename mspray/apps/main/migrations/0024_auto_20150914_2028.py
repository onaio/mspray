# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_auto_20150909_0842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='household',
            name='hh_id',
            field=models.IntegerField(unique=True),
        ),
    ]
