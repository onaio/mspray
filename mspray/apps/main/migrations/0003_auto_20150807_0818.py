# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_district'),
    ]

    operations = [
        migrations.AlterField(
            model_name='district',
            name='houses',
            field=models.IntegerField(db_index=1),
        ),
    ]
