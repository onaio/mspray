# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20150813_0915'),
    ]

    operations = [
        migrations.AddField(
            model_name='targetarea',
            name='district',
            field=models.ForeignKey(default=1, to='main.District'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='district',
            name='code',
            field=models.CharField(max_length=255, unique=True, db_index=1),
        ),
    ]
