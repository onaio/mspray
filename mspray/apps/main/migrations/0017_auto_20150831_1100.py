# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_sprayday_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sprayday',
            name='data',
            field=django_pgjson.fields.JsonField(default={}),
        ),
    ]
