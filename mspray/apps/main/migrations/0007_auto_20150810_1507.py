# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20150810_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='targetarea',
            name='houses',
            field=models.IntegerField(db_index=1),
        ),
    ]
