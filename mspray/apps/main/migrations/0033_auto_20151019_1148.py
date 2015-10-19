# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_auto_20151013_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='spraypoint',
            name='irs_number',
            field=models.CharField(max_length=50, default='XXXXX'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='spraypoint',
            unique_together=set([('data_id', 'location', 'irs_number')]),
        ),
    ]
