# HalfAPI



This Python-based ASGI application aims to provide the core functionality to
multiple API domains.

It's developed at the [LIRMM](https://lirmm.fr) in Montpellier, France.

The name "halfAPI" comes from the deep relationship between it and
[halfORM](https://gite.lirmm.fr/newsi/halfORM), a project authored by
[Joël Maizi](https://gite.lirmm.fr/maizi).

You'll need a database with the API details. You can find the database model in halfapi/models/api.sql

With halfORM's "hop" command, we generate the models that describe the database from the database schema itself. You can find the details in [hop_api](https://gite.lirmm.fr/newsi/db/hop_api) repository.



**NOTE : The authentication module is deeply linked with [auth_lirmm](https://gite.lirmm.fr/newsi/auth_lirmm), so if you need to use the acl.connected function, you will need a running auth_lirmm server to get a token.**

**TODO :** include a token generation tool for testing purpose.



## Dependencies

- python3
- python3-pip
- python3-virtualenv
- python3-venv


### pip

- poetry



## Installing

As the project uses the [poetry]() package manager, you first have to install it globally. It will replace virtualenv, pip, etc...


`pip3 install poetry`


Be sur to include the bin directory of pip in your PATH.

### Virtual Environment (optional)
Then, cd in the halfapi repo, and chose your python version :


`POETRY_VIRTUALENVS_PATH=$HOME/.pyvenv poetry env use 3.7`


**NOTE : The virtualenv will be automatically be activated each time you run a command with the `poetry` tool. If you want to do it the classical way, or even without virtual environment, it's up to your choice.**


Installation of the deps :


`poetry install`


If you need a domain, i.e: organigramme, just add `-E organigramme` to the command.


**NOTE : You need to run `poetry install` before installing any domains (that depends on halfapi).**



## API database

Populate the API database with te server information, the domain's routes, and their ACL by running the following command :


`poetry run halfapi dbupdate`


**NOTE: You need to have the domain's package installed if you want to populate the api routes module, as it check for the existence of the acl functions.**


### Database configuration

The api and domains' databases connection settings are stored by default in `/etc/half_orm`. Check halfORM documentation for more information on how to write these configuration files.

You can set the `HALFORM_SECRET` environment variable if you want to specify an authentication secret.


**TODO :** find a modular way to configure the database connection for each mounted domain



## Running


### Development mode

In the halfapi repository, type :


`poetry run halfapi`


If you need to launch the test suite (only works if you have pytest installed) :


`poetry run pytest`


### Production

The production server may use different init systems. As our main server is Debian-based, we use systemd services to manage the api server. Find the right service files and configure them properly in order to make your production setup perfect.
