[![Build Status](http://drone.onalabs.org/api/badge/github.com/onaio/mspray/status.svg?branch=master)](http://drone.onalabs.org/github.com/onaio/mspray)

mSpray is a mobile based IRS tool developed by Akros with Ona

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

Load team leaders
----------------

    $ python manage.py load_team_leaders data/zambia/team_leaders_2014.csv

Data Flow
---------

- An IRS Form submission is send from ODK Collect to ona.io
- The IRS Form in ona.io has a web service hook configured to transmit the data to the dashboard e.g zambia-2016.mspray.onalabs.org which runs this codebase.
- On receiving the submission:
    - the submission is saved in the SprayDay table
    - the submission will then be linked to a location, these are the options considered in order
        - the OSM file is downloaded and parsed, the OSM information is looked up to see which spray area it falls within, when found the location is the spray area of the submission
        - If that fails, we determine if the area is a new structure, if it is a new structure we lookup the GPS to see which spray area it falls in, if found that becomes the spray area for the submission
        - If that fails, we look up the district and spray area from the submission data corresponding fields, this will then be used for the location of the spray area
        - If that fails, then the submission cannot be linked to a spray area
    - Once a submission has been linked to spray area, a unique record will be created using the spray area, the OSMID or the GPS in the event the submission only captured a GPS.
    - In the event a unique record already existed, the spray status will be checked, if the spray status was 'not sprayed', the new submission will be linked to the unique record, the old record therefore does not become part of the unique record.

Spray Area Calculations
-----------------------
Enumerated Structures - The number of structures as they are in the spray area shape file
Not sprayable structures -  the number of structures in the field that were found not to be sprayable
Duplicate sprayed structures - when a structure has been reported more than one time with the spray status sprayed (if ID XYZ appears twice as sprayed, the count of duplicates will be 1, if it appears 3 times the count will be 2, ... etc.)
Structures on the ground - Enumerated structures subtract number of not sprayable structures + number of new structureres + number of duplicate structures that have been sprayed
Found - Number of all unique records that are sprayable add Number of structures that were sprayed that are not part of the unique record set (i.e the number of duplicates)
Visited Sprayed - Number of all unique records that have the spray status "sprayed"
Spray Effectiveness - percentage of  Visited Sprayed / Structures on the ground
Found Coverage - percentage of Found / Structures on the ground
Sprayed Coverage - percentage of Visited Sprayed / Found
