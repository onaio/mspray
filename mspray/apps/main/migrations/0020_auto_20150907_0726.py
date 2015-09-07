# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_auto_20150902_1004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='code',
            field=models.CharField(max_length=50, unique=True, db_index=1),
        ),
    ]
