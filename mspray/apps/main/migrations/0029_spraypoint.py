# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_sprayday_bgeom'),
    ]

    operations = [
        migrations.CreateModel(
            name='SprayPoint',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('data_id', models.CharField(unique=True, max_length=50)),
                ('sprayday', models.ForeignKey(to='main.SprayDay')),
            ],
        ),
    ]
