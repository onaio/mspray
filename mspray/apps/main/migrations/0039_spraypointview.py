# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


sql = """
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
reverse_sql = """DROP MATERIALIZED VIEW main_spray_point_view;"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0038_spraypointview'),
    ]

    operations = [
        migrations.RunSQL(reverse_sql, sql),
        migrations.RunSQL(sql, reverse_sql)
    ]
