#!/bin/bash

sleep 20

psql -h db -U postgres -c "CREATE ROLE mspray WITH LOGIN PASSWORD 'mspray';"
psql -h db -U postgres -c "CREATE DATABASE mspray OWNER mspray;"
psql -h db -U postgres mspray -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;"

if [ -f /srv/data/initial.schema.sql ]
then
    psql -h db -U mspray mspray -f /srv/data/initial.schema.sql
    mv /srv/data/initial.schema.sql /srv/data/initial.schema.sql.`date +%Y-%m-%d_%s`
fi

if [ -f /srv/data/initial.data.sql ]
then
    psql -h db -U mspray mspray -f /srv/data/initial.data.sql
    mv /srv/data/initial.data.sql /srv/data/initial.data.sql.`date +%Y-%m-%d_%s`
fi

pipenv install
pipenv run python manage.py migrate --noinput
pipenv run python manage.py collectstatic --noinput
pipenv run python manage.py runserver 0.0.0.0:8000
