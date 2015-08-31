# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20150831_0710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='code',
            field=models.CharField(db_index=1, unique=True, max_length=10),
        ),
    ]
