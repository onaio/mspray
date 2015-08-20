# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_teamleader'),
    ]

    operations = [
        migrations.CreateModel(
            name='SprayOperator',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('code', models.SmallIntegerField(unique=True)),
                ('name', models.CharField(max_length=255, db_index=1)),
            ],
        ),
    ]
