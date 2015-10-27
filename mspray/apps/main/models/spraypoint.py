from django.contrib.gis.db import models
from django.db import connection


class SprayPoint(models.Model):
    data_id = models.CharField(max_length=50)
    sprayday = models.ForeignKey('SprayDay')
    location = models.ForeignKey('Location')
    irs_number = models.CharField(max_length=50)

    class Meta:
        app_label = 'main'
        unique_together = (('data_id', 'location', 'irs_number'))

    def __str__(self):
        return self.data_id


MATERIALIZED_VIEW = """
CREATE MATERIALIZED VIEW main_spray_point_view AS (SELECT DISTINCT ON ("main_sprayday"."id") "main_sprayday"."id", (data->>'sprayable_structure') AS "sprayable_structure",
                                          (data->>'sprayable/unsprayed/reason') AS "unsprayed_reason",
                                          (data->>'sprayable/was_sprayed') AS "was_sprayed",
                                          (data->>'sprayable/irs_card_num') AS "irs_card_num",
                                          (data->>'osmstructure') AS "osmstructure",
                                          "main_sprayday"."location_id" as location_id,
                                          "main_location"."code" as location_code,
                                          T3."id" as district_id,
                                          T3."code" as district_code,
                                          "main_sprayday"."team_leader_id",
                                          "main_teamleader"."code" as team_leader_code,
                                          "main_teamleader"."name" as team_leader_name,
                                          "main_sprayday"."spray_operator_id",
                                          "main_sprayoperator"."code" as sprayoperator_code,
                                          "main_sprayday"."spray_date",
                                          "main_sprayday"."start_time",
                                          "main_sprayday"."end_time"
FROM "main_sprayday"
LEFT OUTER JOIN "main_location" ON ("main_sprayday"."location_id" = "main_location"."id")
LEFT OUTER JOIN "main_location" T3 ON ("main_location"."parent_id" = T3."id")
LEFT OUTER JOIN "main_teamleader" ON ("main_sprayday"."team_leader_id" = "main_teamleader"."id")
LEFT OUTER JOIN "main_sprayoperator" ON ("main_sprayday"."spray_operator_id" = "main_sprayoperator"."id")
WHERE "main_sprayday"."id" IN
    (SELECT U0."sprayday_id"
     FROM "main_spraypoint" U0));
"""  # noqa


class SprayPointView(models.Model):
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
    spray_operator_id = models.IntegerField()
    sprayoperator_code = models.CharField(max_length=10)
    spray_date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    district = models.ForeignKey('Location', related_name='districts')
    location = models.ForeignKey('Location', related_name='target_areas')

    class Meta:
        db_table = 'main_spray_point_view'
        managed = False

    @classmethod
    def refresh_view(cls):
        cursor = connection.cursor()
        cursor.execute('REFRESH MATERIALIZED VIEW {} WITH DATA'.format(
            cls._meta.db_table
        ))
