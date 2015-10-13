# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_auto_20151013_1006'),
    ]

    operations = [
        migrations.AddField(
            model_name='spraypoint',
            name='location',
            field=models.ForeignKey(default=1, to='main.Location'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='spraypoint',
            name='data_id',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='spraypoint',
            unique_together=set([('data_id', 'location')]),
        ),
    ]
