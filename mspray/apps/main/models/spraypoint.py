# -*- coding: utf-8 -*-
"""
SprayPoint model.
"""
from django.contrib.gis.db import models


class SprayPoint(models.Model):
    """
    SprayPoint model.
    """

    data_id = models.CharField(max_length=50)
    sprayday = models.ForeignKey("SprayDay", on_delete=models.CASCADE)
    location = models.ForeignKey("Location", on_delete=models.CASCADE)

    class Meta:
        app_label = "main"
        unique_together = ("data_id", "location")

    def __str__(self):
        return self.data_id


MATERIALIZED_VIEW = """
CREATE MATERIALIZED VIEW main_spray_point_view AS (SELECT DISTINCT ON ("main_sprayday"."id") "main_sprayday"."id", (data->>'sprayable_structure') AS "sprayable_structure",
                                          (data->>'sprayable/unsprayed/reason') AS "unsprayed_reason",
                                          (data->>'sprayable/was_sprayed') AS "was_sprayed",
                                          (data->>'sprayable/irs_card_num') AS "irs_card_num",
                                          (data->>'osmstructure') AS "osmstructure",
                                          (data->>'sprayformid') AS "sprayformid",
                                          "main_sprayday"."location_id" AS location_id,
                                          "main_location"."code" AS location_code,
                                          T3."id" AS district_id,
                                          T3."code" AS district_code,
                                          "main_sprayday"."team_leader_id",
                                          "main_teamleader"."code" AS team_leader_code,
                                          "main_teamleader"."name" AS team_leader_name,
                                          "main_teamleaderassistant"."code" AS team_leader_assistant_code,
                                          "main_sprayday"."spray_operator_id",
                                          "main_sprayoperator"."code" AS sprayoperator_code,
                                          "main_sprayday"."spray_date",
                                          "main_sprayday"."start_time",
                                          "main_sprayday"."end_time"
FROM "main_sprayday"
LEFT OUTER JOIN "main_location" ON ("main_sprayday"."location_id" = "main_location"."id")
LEFT OUTER JOIN "main_location" T3 ON ("main_location"."parent_id" = T3."id")
LEFT OUTER JOIN "main_teamleader" ON ("main_sprayday"."team_leader_id" = "main_teamleader"."id")
LEFT OUTER JOIN "main_teamleaderassistant" ON ("main_sprayday"."team_leader_assistant_id" = "main_teamleaderassistant"."id")
LEFT OUTER JOIN "main_sprayoperator" ON ("main_sprayday"."spray_operator_id" = "main_sprayoperator"."id")
WHERE "main_sprayday"."id" IN
    (SELECT U0."sprayday_id"
     FROM "main_spraypoint" U0));
"""  # noqa


class SprayPointView(models.Model):
    """
    SprayPointView materialized view model.
    """
    sprayable_structure = models.CharField(max_length=10)
    was_sprayed = models.CharField(max_length=10)
    irs_card_num = models.CharField(max_length=10)
    osmstructure = models.CharField(max_length=50)
    unsprayed_reason = models.CharField(max_length=50)
    location_code = models.CharField(max_length=50)
    district_code = models.CharField(max_length=50)
    team_leader_id = models.IntegerField()
    team_leader_code = models.CharField(max_length=50)
    team_leader_name = models.CharField(max_length=255)
    team_leader_assistant_code = models.CharField(max_length=50)
    spray_operator_id = models.IntegerField()
    sprayoperator_code = models.CharField(max_length=10)
    spray_date = models.DateField()
    start_time = models.DateTimeField()
    sprayformid = models.CharField(max_length=50)
    end_time = models.DateTimeField()
    district = models.ForeignKey(
        "Location", related_name="districts", on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        "Location", related_name="target_areas", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "main_spray_point_view"
        managed = False

    @classmethod
    def refresh_view(cls):
        # cursor = connection.cursor()
        # cursor.execute('REFRESH MATERIALIZED VIEW {} WITH DATA'.format(
        #     cls._meta.db_table
        # ))
        pass


def refresh_materialized_view(sender, **kwargs):  # pylint: disable=W0613
    """
    Refresh the materialized view SprayPointView.
    """
    SprayPointView.refresh_view()


# post_save.connect(refresh_materialized_view, sender=SprayPoint)


class Hhcsv(models.Model):
    """
    Household CSV model.
    """

    osmid = models.IntegerField()
    y = models.FloatField()  # pylint: disable=invalid-name
    x3 = models.FloatField()  # pylint: disable=invalid-name
    shape_area = models.FloatField()
    shape_length = models.FloatField()

    class Meta:
        db_table = "households"
        managed = False


class OsmData(models.Model):
    """
    OsmData model.
    """

    osmid = models.IntegerField()
    target_area = models.CharField(max_length=100)
    district = models.CharField(max_length=20)
    building = models.CharField(max_length=3)
    shape_area = models.FloatField()
    shape_length = models.FloatField()

    class Meta:
        db_table = "osm_data"
        managed = False


class MatchedData(models.Model):
    """
    MatchedData model.
    """

    osmpk = models.IntegerField(unique=True)
    osmid = models.IntegerField()
    target_area = models.CharField(max_length=100)
    district = models.CharField(max_length=20)
    building = models.CharField(max_length=3)
    shape_area = models.FloatField()
    shape_length = models.FloatField()
    y = models.FloatField()  # pylint: disable=invalid-name
    x3 = models.FloatField()  # pylint: disable-invalid-name
