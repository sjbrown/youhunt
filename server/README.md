# Instructions

(from https://docs.docker.com/compose/django/)

## Install Docker
## Install docker-compose


## Build the project:

Open a terminal in this directory.

`docker-compose run --rm web django-admin.py startproject yweb .`

This creates manage.py (It will warn you about not overwriting files
in yweb/. That's fine.)

`docker-compose run --rm web python manage.py syncdb`

This creates the databases.

Change the permissions to `.` so that you own everything: `sudo chown -R $USER .`


## Start it running:

`docker-compose up`


## Shortcuts:

Consider adding an alias yhserver="docker-compose run --rm web"

