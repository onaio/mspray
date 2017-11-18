#!/bin/bash

sleep 20

psql -h db -U postgres -c "CREATE ROLE mspray WITH LOGIN PASSWORD 'mspray';"
psql -h db -U postgres -c "CREATE DATABASE mspray OWNER mspray;"
psql -h db -U postgres mspray -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;"

. /srv/.virtualenv/bin/activate

cd /srv/mspray
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
