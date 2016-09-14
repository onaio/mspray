# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-09-14 08:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_node_tag_way_waytag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='node_id',
            field=models.CharField(max_length=25, unique=True),
        ),
        migrations.AlterField(
            model_name='node',
            name='timestamp',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='node',
            name='user',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='way',
            name='way_id',
            field=models.CharField(max_length=25, unique=True),
        ),
    ]
