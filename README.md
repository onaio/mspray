mSpray
=======

mSpray is a mobile based IRS tool developed by Akros with Ona

Setup
-----

**INSTALLATION**

------------------------------------------------------------------------

**Get the Code**

------------------------------------------------------------------------

```
git clone git\@github.com:onaio/mspray.git

```

**Docker**

------------------------------------------------------------------------

Install Docker and Docker Compose. Run the following command to start
the containers in the background and leave them running. The option -d
runs in detach mode. Detached mode: Run containers in the background and
prints new container names.

```

docker-compose up -d

```

```

docker-compose logs -f

```

Running docker-compose logs -f, could be useful when you need to follow the 
log output from services.



It should now be accessible via http://localhost:8000.


**Running the docker container**

The following command can be used to interact with the docker container on the command line.  -it specifies that we will be interacting with that container through the bash or any other shell preferable to you.  

```

docker exec -it mspray_queue_1 bash


```

**set up a virtual envirenment**

------------------------------------------------------------------------

For you to run the following command, you mast have pipenv installed:

```

pipenv shell

```


**Run tests**

Consequently, we could use the following commands to run tests associatted with the project.

```

python manage.py test

```

**Obtaining sufficient privileges**

Get your psql utility running by running the following command. The following command connects to a database under a specific user 'postgres', who is able to grant priviledges to the mspray user

```

psql -h db -U postgres

```

Depending on your configuration, this section describes several methods to configure the database user with sufficient privileges to run tests for the mspray application on PostgreSQL. Your testing database user needs to have the ability to create databases. In other configurations, you may be required to use a database superuser as only superusers can create the extension or update it to a new version. If it is set to false, just the privileges required to execute the commands in the installation or update script are required.

```

ALTER USER mspray WITH SUPERUSER;

```


**For Development Use-cases** 

The following packages need to be installed to run tests. 
Note, this is unnecessary for those who do not need to run tests while setting up.

```

pipenv install --dev

```


Afterwards run the following management commands to load relevant data into the application.

```

python manage.py load_location_shape_file mspray/apps/main/tests/fixtures/Lusaka/districts/Lusaka.shp NAME district --parent-skip=yes


python manage.py load_location_shape_file mspray/apps/main/tests/fixtures/Lusaka/HF/Mtendere.shp HFC_NAME RHC --parent=DISTRICT --parent-level=district


python manage.py load_location_shape_file mspray/apps/main/tests/fixtures/Lusaka/SA/Akros_1.shp SPRAYAREA ta --parent=HFC_NAME --parent-level=RHC --structures=HOUSES


```

These three commands from the load_location_shape_file custom management command are used to loads districts, health facility catchment area and spray area shapefiles.


```

python manage.py load_osm_hh mspray/apps/main/tests/fixtures/Lusaka/OSM/

```

The load_osm_hh command Loads OSM files as households into the Household model. This then loads the structures found in the region


Finally use this command to update location structure numbers for districts/regions from target areas 

```

python manage.py update_locations_structures

```



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
