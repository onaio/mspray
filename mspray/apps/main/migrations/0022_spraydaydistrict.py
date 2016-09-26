# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-21 06:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_spraydayhealthcenterlocation'),
    ]

    operations = [
        migrations.CreateModel(
            name='SprayDayDistrict',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.SprayDay')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Location')),
            ],
        ),
    ]