-- source: http://sorokine.blogspot.nl/2011/05/postgis-function-for-random-point.html
CREATE OR REPLACE FUNCTION RandomPoint (
  geom Geometry,
  maxiter INTEGER DEFAULT 1000
 )
 RETURNS Geometry
 AS $$
DECLARE
 i INTEGER := 0;
 x0 DOUBLE PRECISION;
 dx DOUBLE PRECISION;
 y0 DOUBLE PRECISION;
 dy DOUBLE PRECISION;
 xp DOUBLE PRECISION;
 yp DOUBLE PRECISION;
 rpoint Geometry;
BEGIN
 -- find envelope
 x0 = ST_XMin(geom);
 dx = (ST_XMax(geom) - x0);
 y0 = ST_YMin(geom);
 dy = (ST_YMax(geom) - y0);

 WHILE i < maxiter LOOP
  i = i + 1;
  xp = x0 + dx * random();
  yp = y0 + dy * random();
  rpoint = ST_SetSRID( ST_MakePoint( xp, yp ), ST_SRID(geom) );
  EXIT WHEN ST_Within( rpoint, geom );
 END LOOP;

 IF i >= maxiter THEN
  RAISE EXCEPTION 'RandomPoint: number of interations exceeded ', maxiter;
 END IF;

 RETURN rpoint;
END;
$$ LANGUAGE plpgsql;

--
-- a variation of random point function that works more reliably with
-- sparse unbalanced multigeometries
--
CREATE OR REPLACE FUNCTION RandomPointMulti (
  geom Geometry
 )
 RETURNS Geometry
 AS $$
DECLARE
 maxiter INTEGER := 100000;
 i INTEGER := 0;
 n INTEGER := 0; -- total number of geometries in collection
 g INTEGER := 0; -- geometry number in collection to find random point in
 total_area DOUBLE PRECISION; -- total area
 cgeom Geometry;
BEGIN
 total_area = ST_Area(geom);
 n = ST_NumGeometries(geom);

 WHILE i < maxiter LOOP
  i = i + 1;
  g = floor(random() * n)::int;
  cgeom = ST_GeometryN(geom, g); -- weight the probability of selecting a geometry by its relative area
  IF random() < ST_Area(cgeom)/total_area THEN
   RETURN RandomPoint( cgeom );
  END IF;
 END LOOP;

 RAISE EXCEPTION 'RandomPointMulti: too many iterations';
END;
$$ LANGUAGE plpgsql;
