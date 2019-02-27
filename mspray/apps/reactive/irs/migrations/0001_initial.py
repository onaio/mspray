# Generated by Django 2.1.3 on 2019-02-27 12:48

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [("main", "0062_performancereport_data")]

    operations = [
        migrations.CreateModel(
            name="CommunityHealthWorker",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("modified_on", models.DateTimeField(auto_now=True)),
                ("code",
                 models.CharField(db_index=True, max_length=50, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("geom",
                 django.contrib.gis.db.models.fields.PointField(srid=4326)),
                (
                    "bgeom",
                    django.contrib.gis.db.models.fields.GeometryField(
                        null=True, srid=4326),
                ),
                (
                    "location",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chw",
                        to="main.Location",
                    ),
                ),
            ],
            options={
                "verbose_name": "Community Health Worker",
                "verbose_name_plural": "Community Health Workers",
            },
        )
    ]
