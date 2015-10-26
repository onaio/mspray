# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_auto_20151026_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='sprayoperator',
            name='team_leader',
            field=models.ForeignKey(to='main.TeamLeader', null=True),
        ),
    ]
