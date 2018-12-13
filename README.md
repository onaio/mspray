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
git clone git@github.com:onaio/mspray.git

```

**Docker**

------------------------------------------------------------------------

You need to have Docker and Docker Compose installed on your machine. 
Run the following commands to start the containers in the background and leave them running.
The option -d runs in detach mode(runs the containers in the background).

```

docker-compose up -d

```


Running docker-compose logs -f, could be useful when you need to follow the log output from services.

```

docker-compose logs -f

```


You can use `docker exec` command to start a shell inside the running container. For example:


```

docker exec -it mspray_web_1 bash


```  

The above command starts the bash shell inside the `mspray_web_1` container. 


It should now be accessible via:

```

http://localhost:8000.

```

**For Development Use-cases** 

The following packages need to be installed to set up a development environment. 
Note, this is unnecessary for those who do not need to run tests while setting up.


For you to run the following command, you must have Pipenv installed:

```

pipenv install --dev

```


Use `python manage.py test` to now run tests.


**Setting up Postgres**

Once you have docker running and are able to get into a container shell environment, you will need to apply the superuser privileges for the mspray database user. 
Use the `postgres` user to grant privileges to the `mspray` user.

```

psql -h db -U postgres

```

Within on your database configuration, the postgres user must have sufficient privileges to run tests i.e. the user needs to have the ability to create testing databases. 

The following command grants the postgres user role with superuser priviledges. 

```

ALTER USER mspray WITH SUPERUSER;

```

You can  now load some fixtures to your mspray dashboard, this gives you the chance to explore the mspray dashboard.

```

python manage.py load_location_shape_file mspray/apps/main/tests/fixtures/Lusaka/districts/Lusaka.shp NAME district --parent-skip=yes


python manage.py load_location_shape_file mspray/apps/main/tests/fixtures/Lusaka/HF/Mtendere.shp HFC_NAME RHC --parent=DISTRICT --parent-level=district


python manage.py load_location_shape_file mspray/apps/main/tests/fixtures/Lusaka/SA/Akros_1.shp SPRAYAREA ta --parent=HFC_NAME --parent-level=RHC --structures=HOUSES


```

The above three commands will load the districts, health facility catchment areas and spray area locations from the shape files provided.


```

python manage.py load_osm_hh mspray/apps/main/tests/fixtures/Lusaka/OSM/

```

The load_osm_hh command Loads OSM files as households into the Household model. This then loads the structures found in the region.


Finally use this command to update location structure numbers for districts/regions within the target areas.

```

python manage.py update_locations_structures

```



Data Flow
---------

- An IRS Form submission is sent from ODK Collect to ona.io
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

![data_flow](https://user-images.githubusercontent.com/11174326/49940782-9bd80880-fef1-11e8-8ad4-f3ec41c5c00e.png)


Spray Area Calculations
-----------------------

|**Variable** | **Aggregations**         |
| ------------- | ----------- |
| Enumerated Structures             | The number of structures as they are in the spray area shape file.|
| Not sprayable structures          | The number of structures in the field that were found not to be sprayable.     |
| Duplicate sprayed structures      | When a structure has been reported more than one time with the spray status sprayed (if                                         ID XYZ appears twice as sprayed, the count of duplicates will be 1, if it appears 3 times                                       the count will be 2, ... etc.)     |
| Structures on the ground     | Enumerated structures subtract the number of not sprayable structures + number of new                                          structures + number of duplicate structures that have been sprayed.     |
| Found     | Number of all unique records that are sprayable add Number of structures that were sprayed that are not part of                 the unique record set (i.e the number of duplicates.)     |
| Visited Sprayed     | Number of all unique records that have the spray status "sprayed".     |
| Spray Effectiveness     | The percentage of  Visited Sprayed / Structures on the ground.     |
| Found Coverage     | The percentage of Found / Structures on the ground.     |
| Sprayed Coverage     | The percentage of Visited Sprayed / Found.     |

