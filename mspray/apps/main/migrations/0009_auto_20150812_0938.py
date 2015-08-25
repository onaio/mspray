# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20150812_0937'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='household',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='household',
            name='comment_1',
        ),
        migrations.RemoveField(
            model_name='household',
            name='descr',
        ),
        migrations.RemoveField(
            model_name='household',
            name='hh_type',
        ),
        migrations.RemoveField(
            model_name='household',
            name='name',
        ),
        migrations.RemoveField(
            model_name='household',
            name='orig_fid',
        ),
        migrations.RemoveField(
            model_name='household',
            name='type_1',
        ),
    ]
