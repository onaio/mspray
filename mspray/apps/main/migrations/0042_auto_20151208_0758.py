# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0041_merge'),
    ]

    operations = [
        migrations.RunSQL('TRUNCATE main_spraypoint'),
        migrations.AlterUniqueTogether(
            name='spraypoint',
            unique_together=set([('data_id', 'location')]),
        ),
        migrations.RemoveField(
            model_name='spraypoint',
            name='irs_number',
        ),
    ]
