# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_hhcsv_matcheddata_osmdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='matcheddata',
            name='osmpk',
            field=models.IntegerField(unique=True, default=1),
            preserve_default=False,
        ),
    ]
