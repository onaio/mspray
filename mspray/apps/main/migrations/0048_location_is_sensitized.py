# Generated by Django 2.1.1 on 2018-09-30 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0047_sensitizationvisit_household'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='is_sensitized',
            field=models.BooleanField(null=True),
        ),
    ]
