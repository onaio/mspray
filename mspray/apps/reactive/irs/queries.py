"""Reactive IRS queries module"""

from django.db import connection

from mspray.apps.main.serializers.target_area import dictfetchall
from mspray.apps.main.utils import parse_spray_date

SPRAY_AREA_INDICATOR_SQL = """
SELECT
COALESCE(SUM(CASE WHEN "other" > 0 THEN 1 ELSE 0 END),0) AS "other",
COALESCE(SUM(CASE WHEN "not_sprayable" > 0 THEN 1 ELSE 0 END),0) AS "not_sprayable",
COALESCE(SUM(CASE WHEN "found" > 0 THEN 1 ELSE 0 END),0) AS "found",
COALESCE(SUM(CASE WHEN "sprayed" > 0 THEN 1 ELSE 0 END),0) AS "sprayed",
COALESCE(SUM(CASE WHEN "new_structures" > 0 THEN 1 ELSE 0 END),0) AS "new_structures",
COALESCE(SUM(CASE WHEN "not_sprayed" > 0 THEN 1 ELSE 0 END),0) AS "not_sprayed",
COALESCE(SUM(CASE WHEN "refused" >0 THEN 1 ELSE 0 END),0) AS "refused" FROM
(
  SELECT
  SUM(CASE WHEN (("main_sprayday"."data" @> '{"osmstructure:notsprayed_reASon": "refused"}' OR "main_sprayday"."data" @> '{"newstructure/gps_osm_file:notsprayed_reason": "refused"}') AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = false) THEN 0 WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = true) THEN 0 ELSE 1 END) AS "other",
  SUM(CASE WHEN ("main_sprayday"."data" ? 'osmstructure:way:id' AND "main_sprayday"."sprayable" = false AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."household_id" IS NOT NULL) THEN 1 ELSE 0 END) AS "not_sprayable",
  SUM(CASE WHEN ("main_sprayday"."data" ? 'osmstructure:way:id' AND "main_sprayday"."sprayable" = false AND "main_spraypoint"."id" IS NOT NULL) THEN 0 WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL) THEN 1 WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NULL AND "main_sprayday"."was_sprayed" = true) THEN 1 ELSE 0 END) AS "found",
  SUM(CASE WHEN ("main_sprayday"."sprayable" = true AND "main_sprayday"."was_sprayed" = true) THEN 1 ELSE 0 END) AS "sprayed",
  SUM(CASE WHEN ("main_sprayday"."data" ? 'newstructure/gps' AND "main_sprayday"."sprayable" = true) THEN 1 WHEN (("main_sprayday"."data" ? 'osmstructure:node:id' OR "main_sprayday"."data" ? 'newstructure/gps_osm_file:node:id') AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL) THEN 1 WHEN (("main_sprayday"."data" ? 'osmstructure:node:id' OR "main_sprayday"."data" ? 'newstructure/gps_osm_file:node:id') AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NULL AND "main_sprayday"."was_sprayed" = true) THEN 1 WHEN ("main_sprayday"."data" ? 'osmstructure:way:id' AND "main_sprayday"."sprayable" = true AND "main_sprayday"."household_id" IS NULL) THEN 1 ELSE 0 END) AS "new_structures",
  SUM(CASE WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = false) THEN 1 ELSE 0 END) AS "not_sprayed",
  SUM(CASE WHEN (("main_sprayday"."data" @> '{"osmstructure:notsprayed_reASon": "refused"}' OR "main_sprayday"."data" @> '{"newstructure/gps_osm_file:notsprayed_reason": "refused"}') AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = false) THEN 1 ELSE 0 END) AS "refused"
  FROM "main_sprayday" LEFT OUTER JOIN "main_spraypoint" ON ("main_sprayday"."id" = "main_spraypoint"."sprayday_id") WHERE (ST_CoveredBy("main_sprayday"."geom", ST_GeomFromEWKB(%s))) GROUP BY "main_sprayday"."id"
) AS "sub_query";
"""  # noqa

SPRAY_AREA_INDICATOR_SQL_DATE_FILTERED = """
SELECT
COALESCE(SUM(CASE WHEN "other" > 0 THEN 1 ELSE 0 END),0) AS "other",
COALESCE(SUM(CASE WHEN "not_sprayable" > 0 THEN 1 ELSE 0 END),0) AS "not_sprayable",
COALESCE(SUM(CASE WHEN "found" > 0 THEN 1 ELSE 0 END),0) AS "found",
COALESCE(SUM(CASE WHEN "sprayed" > 0 THEN 1 ELSE 0 END),0) AS "sprayed",
COALESCE(SUM(CASE WHEN "new_structures" > 0 THEN 1 ELSE 0 END),0) AS "new_structures",
COALESCE(SUM(CASE WHEN "not_sprayed" > 0 THEN 1 ELSE 0 END),0) AS "not_sprayed",
COALESCE(SUM(CASE WHEN "refused" >0 THEN 1 ELSE 0 END),0) AS "refused" FROM
(
  SELECT
  SUM(CASE WHEN (("main_sprayday"."data" @> '{"osmstructure:notsprayed_reASon": "refused"}' OR "main_sprayday"."data" @> '{"newstructure/gps_osm_file:notsprayed_reason": "refused"}') AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = false) THEN 0 WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = true) THEN 0 ELSE 1 END) AS "other",
  SUM(CASE WHEN ("main_sprayday"."data" ? 'osmstructure:way:id' AND "main_sprayday"."sprayable" = false AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."household_id" IS NOT NULL) THEN 1 ELSE 0 END) AS "not_sprayable",
  SUM(CASE WHEN ("main_sprayday"."data" ? 'osmstructure:way:id' AND "main_sprayday"."sprayable" = false AND "main_spraypoint"."id" IS NOT NULL) THEN 0 WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL) THEN 1 WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NULL AND "main_sprayday"."was_sprayed" = true) THEN 1 ELSE 0 END) AS "found",
  SUM(CASE WHEN ("main_sprayday"."sprayable" = true AND "main_sprayday"."was_sprayed" = true) THEN 1 ELSE 0 END) AS "sprayed",
  SUM(CASE WHEN ("main_sprayday"."data" ? 'newstructure/gps' AND "main_sprayday"."sprayable" = true) THEN 1 WHEN (("main_sprayday"."data" ? 'osmstructure:node:id' OR "main_sprayday"."data" ? 'newstructure/gps_osm_file:node:id') AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL) THEN 1 WHEN (("main_sprayday"."data" ? 'osmstructure:node:id' OR "main_sprayday"."data" ? 'newstructure/gps_osm_file:node:id') AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NULL AND "main_sprayday"."was_sprayed" = true) THEN 1 WHEN ("main_sprayday"."data" ? 'osmstructure:way:id' AND "main_sprayday"."sprayable" = true AND "main_sprayday"."household_id" IS NULL) THEN 1 ELSE 0 END) AS "new_structures",
  SUM(CASE WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = false) THEN 1 ELSE 0 END) AS "not_sprayed",
  SUM(CASE WHEN (("main_sprayday"."data" @> '{"osmstructure:notsprayed_reASon": "refused"}' OR "main_sprayday"."data" @> '{"newstructure/gps_osm_file:notsprayed_reason": "refused"}') AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = false) THEN 1 ELSE 0 END) AS "refused"
  FROM "main_sprayday" LEFT OUTER JOIN "main_spraypoint" ON ("main_sprayday"."id" = "main_spraypoint"."sprayday_id") WHERE (ST_CoveredBy("main_sprayday"."geom", ST_GeomFromEWKB(%s)) AND "main_sprayday"."spray_date" <= %s::date) GROUP BY "main_sprayday"."id"
) AS "sub_query";
"""  # noqa

SPRAY_AREA_INDICATOR_SQL_WEEK = """
SELECT
COALESCE(SUM(CASE WHEN "other" > 0 THEN 1 ELSE 0 END),0) AS "other",
COALESCE(SUM(CASE WHEN "not_sprayable" > 0 THEN 1 ELSE 0 END),0) AS "not_sprayable",
COALESCE(SUM(CASE WHEN "found" > 0 THEN 1 ELSE 0 END),0) AS "found",
COALESCE(SUM(CASE WHEN "sprayed" > 0 THEN 1 ELSE 0 END),0) AS "sprayed",
COALESCE(SUM(CASE WHEN "new_structures" > 0 THEN 1 ELSE 0 END),0) AS "new_structures",
COALESCE(SUM(CASE WHEN "not_sprayed" > 0 THEN 1 ELSE 0 END),0) AS "not_sprayed",
COALESCE(SUM(CASE WHEN "refused" >0 THEN 1 ELSE 0 END) AS,0) "refused" FROM
(
  SELECT
  SUM(CASE WHEN (("main_sprayday"."data" @> '{"osmstructure:notsprayed_reASon": "refused"}' OR "main_sprayday"."data" @> '{"newstructure/gps_osm_file:notsprayed_reason": "refused"}') AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = false) THEN 0 WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = true) THEN 0 ELSE 1 END) AS "other",
  SUM(CASE WHEN ("main_sprayday"."data" ? 'osmstructure:way:id' AND "main_sprayday"."sprayable" = false AND "main_spraypoint"."id" IS NOT NULL) THEN 1 ELSE 0 END) AS "not_sprayable",
  SUM(CASE WHEN ("main_sprayday"."data" ? 'osmstructure:way:id' AND "main_sprayday"."sprayable" = false AND "main_spraypoint"."id" IS NOT NULL) THEN 0 WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL) THEN 1 WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NULL AND "main_sprayday"."was_sprayed" = true) THEN 1 ELSE 0 END) AS "found",
  SUM(CASE WHEN ("main_sprayday"."sprayable" = true AND "main_sprayday"."was_sprayed" = true) THEN 1 ELSE 0 END) AS "sprayed",
  SUM(CASE WHEN ("main_sprayday"."data" ? 'newstructure/gps' AND "main_sprayday"."sprayable" = true) THEN 1 WHEN (("main_sprayday"."data" ? 'osmstructure:node:id' OR "main_sprayday"."data" ? 'newstructure/gps_osm_file:node:id') AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL) THEN 1 WHEN (("main_sprayday"."data" ? 'osmstructure:node:id' OR "main_sprayday"."data" ? 'newstructure/gps_osm_file:node:id') AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NULL AND "main_sprayday"."was_sprayed" = true) THEN 1 ELSE 0 END) AS "new_structures",
  SUM(CASE WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = false) THEN 1 ELSE 0 END) AS "not_sprayed",
  SUM(CASE WHEN (("main_sprayday"."data" @> '{"osmstructure:notsprayed_reASon": "refused"}' OR "main_sprayday"."data" @> '{"newstructure/gps_osm_file:notsprayed_reason": "refused"}') AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = false) THEN 1 ELSE 0 END) AS "refused"
  FROM "main_sprayday" LEFT OUTER JOIN "main_spraypoint" ON
  ("main_sprayday"."id" = "main_spraypoint"."sprayday_id") WHERE
  (ST_CoveredBy("main_sprayday"."geom", ST_GeomFromEWKB(%s)) AND EXTRACT('week' FROM "main_sprayday"."spray_date") <= %s) GROUP BY "main_sprayday"."id"
) AS "sub_query";
"""  # noqa


def get_spray_data_using_geoquery(location: object, context: object = None):
    """
    Get spray data of a location using a geoquery
    """
    if not context:
        context = {}

    request = context.get("request")
    spray_date = parse_spray_date(request) if request else None
    week_number = context.get("week_number")

    cursor = connection.cursor()

    if spray_date:
        cursor.execute(
            SPRAY_AREA_INDICATOR_SQL_DATE_FILTERED,
            [location.geom.ewkb,
             spray_date.strftime("%Y-%m-%d")],
        )
    elif week_number:
        cursor.execute(SPRAY_AREA_INDICATOR_SQL_WEEK,
                       [location.geom.ewkb, week_number])
    else:
        cursor.execute(SPRAY_AREA_INDICATOR_SQL, [location.geom.ewkb])
    results = dictfetchall(cursor)

    return results[0]
