[![Build Status](http://drone.onalabs.org/api/badge/github.com/onaio/mspray/status.svg?branch=master)](http://drone.onalabs.org/github.com/onaio/mspray)

mSpray projects
===============

Setup
-----

Install required packages and create database.

    fab system_setup:default,dbname=dbname,dbuser=dbusername,dbpass=dbpassword

Setup codebase and initial server configuration
    fab server_setup:default,branch=gitbranch,dbuser=dbusername,dbpass=dbpassword,dbname=dbname,port=uwsgiport,project=countryname

Deploying
---------

Applying changes to deployed project
    fab deploy:default,branch=gitbranch,dbuser=dbusername,dbpass=dbpassword,dbname=dbname,port=uwsgiport,project=countryname

Project
-------

- 2014 Zambia, port=8008, branch=mspray2014
- 2015 Zambia, port=8013, branch=district-perfomace
- 2015 Madagascar, port=8012, branch=madagascar
- 2015 Namibia, port=8011, branch=master
