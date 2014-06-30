FROM ubuntu

MAINTAINER Ukang'a Dickson

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -yqq python3 python3-dev python3-setuptools python3-pip git-core libpq-dev libproj-dev gdal-bin
RUN apt-get install -yqq supervisor

RUN mkdir -p /var/www
ADD . /var/www/mspray

RUN chmod +x /var/www/mspray/scripts/start
RUN pip3 install -r /var/www/mspray/requirements.pip
RUN ln -s /var/www/mspray/supervisor-app.conf /etc/supervisor/conf.d/
RUN mkdir -p /var/log/uwsgi

ENV DJANGO_SETTINGS_MODULE mspray.preset.local_settings

EXPOSE 8000

CMD ["/var/www/mspray/scripts/start"]
