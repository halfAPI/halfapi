# halfAPI

This Python-based ASGI application aims to provide the core functionality to
multiple API domains.

It's developed at the [LIRMM](https://lirmm.fr) in Montpellier, France.

The name "halfAPI" comes from the deep relationship between it and
[halfORM](https://gite.lirmm.fr/newsi/halfORM), a project authored by 
[Joël Maizi](https://gite.lirmm.fr/maizi).


## how-to

As the project uses the [poetry]() package manager, you first have to install it globally. It will replace virtualenv, pip, etc...

`pip install poetry`

Be sur to include the bin directory of pip in your PATH.


Then, cd in the halfapi repo, and chose your python version :

`poetry env use 3.8`

- at this point, every time you come into the folder, when you launch something with "poetry run", it is launched within the virtual environment for this project -

And install the deps :

`poetry install`

If you need a domain, i.e: organigramme, just add *-E organigramme* avec *install*.

`poetry install -E organigramme`

Then, to run the server :

`poetry run halfapi`


If you need to launch the test suite (only works if you have pytest installed) :

`poetry run pytest`

# API database

You just need to run the following command to insert the right data into the api database :

`poetry run halfapi dbupdate`

# API database configuration

You can set the HALFORM_SECRET and HALFORM_DSN variables to setup the way you connect to the API database.

HALFORM_SECRET="wtfqwertz"
HALFORM_DSN="dbname=api user=api password=api host=127.0.0.1 port=5432"

## Warning

For the domains' databases, for now the database connection string is hardcoded (check app.mount_domains).

@TODO find a modular way to configure the database connection for each mounted domain
