# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_district_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamLeader',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('code', models.SmallIntegerField(unique=True)),
                ('name', models.CharField(max_length=255, db_index=1)),
            ],
        ),
    ]
