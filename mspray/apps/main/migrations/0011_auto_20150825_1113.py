# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='targetarea',
            name='targetid',
            field=models.CharField(max_length=50, db_index=1),
        ),
    ]
