# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20150807_0818'),
    ]

    operations = [
        migrations.AddField(
            model_name='district',
            name='code',
            field=models.CharField(default='CODE', max_length=10, db_index=1),
            preserve_default=False,
        ),
    ]
