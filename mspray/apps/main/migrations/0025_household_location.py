# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_auto_20150914_2028'),
    ]

    operations = [
        migrations.AddField(
            model_name='household',
            name='location',
            field=models.ForeignKey(to='main.Location', default=1),
        ),
    ]
