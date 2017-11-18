FROM ubuntu:16.04

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && apt-get install -y postgresql-client \
    binutils \
    libproj-dev \
    gdal-bin \
    memcached \
    libmemcached-dev \
    build-essential \
    python3.5 \
    python3-pip \
    python3.5-dev \
    python-virtualenv \
    git \
    libssl-dev \
    gfortran \
    libatlas-base-dev \
    libxml2-dev \
    libxslt-dev \
    libpq-dev

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN mkdir -p /srv/mspray

ADD requirements.pip /srv/mspray/

WORKDIR /srv/mspray

RUN virtualenv -p `which python3` /srv/.virtualenv
RUN . /srv/.virtualenv/bin/activate; \
    pip install pip --upgrade && pip install pip-tools && pip-sync requirements.pip

ADD . /srv/mspray/

ENV DJANGO_SETTINGS_MODULE mspray.preset.docker

RUN rm -rf /var/lib/apt/lists/* \
  && find . -name '*.pyc' -type f -delete

CMD ["/srv/mspray/docker/docker-entrypoint.sh"]
