#!/bin/bash

sleep 20

if [ -f .env ]
then
    . .env
fi
psql -h db -U postgres -c "CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASS}';"
psql -h db -U postgres -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"
psql -h db -U postgres $DB_NAME -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;"

if [ -f /srv/data/initial.schema.sql ]
then
    psql -h db -U $DB_USER $DB_NAME -f /srv/data/initial.schema.sql
    mv /srv/data/initial.schema.sql /srv/data/initial.schema.sql.`date +%Y-%m-%d_%s`
fi

if [ -f /srv/data/initial.data.sql ]
then
    psql -h db -U $DB_USER $DB_NAME -f /srv/data/initial.data.sql
    mv /srv/data/initial.data.sql /srv/data/initial.data.sql.`date +%Y-%m-%d_%s`
fi

pipenv install
pipenv run python manage.py migrate --noinput
pipenv run python manage.py collectstatic --noinput
pipenv run python manage.py runserver 0.0.0.0:8000
