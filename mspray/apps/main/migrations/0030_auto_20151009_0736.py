# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_spraypoint'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='householdsbuffer',
            name='target_area',
        ),
        migrations.AddField(
            model_name='householdsbuffer',
            name='location',
            field=models.ForeignKey(default=1, to='main.Location'),
            preserve_default=False,
        ),
    ]
