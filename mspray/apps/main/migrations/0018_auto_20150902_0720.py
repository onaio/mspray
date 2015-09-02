# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20150831_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teamleader',
            name='code',
            field=models.CharField(unique=True, max_length=10),
        ),
    ]
