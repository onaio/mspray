FROM ubuntu:18.04

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
    python3.6 \
    python3-pip \
    python3.6-dev \
    python-virtualenv \
    git \
    libssl-dev \
    gfortran \
    libatlas-base-dev \
    libxml2-dev \
    libxslt-dev \
    libpq-dev \
    locales \
    tmux

RUN locale-gen en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
RUN dpkg-reconfigure locales

RUN rm -rf /var/lib/apt/lists/* \
  && find . -name '*.pyc' -type f -delete

RUN useradd -m mspray
RUN mkdir -p /srv/mspray && chown mspray:mspray /srv/mspray
WORKDIR /srv/mspray
USER mspray
RUN pip3 install --user pipenv
RUN echo "set-option -g default-shell /bin/bash" > ~/.tmux.conf
ADD . /srv/mspray

ENV PATH /home/mspray/.local/bin:$PATH
ENV DJANGO_SETTINGS_MODULE mspray.preset.docker
CMD ["/srv/mspray/docker/docker-entrypoint.sh"]
