#!/usr/bin/env python3
import os
from os import environ
from configparser import ConfigParser

__version__ = '0.1.0'
print(f'HalfAPI version:{__version__}')

config = ConfigParser(defaults={
    'project': {
        'host': '127.0.0.1',
        'port': '8000',
        'secret': None,
        'base_dir': None,
        'production': False
    }
})
config.read(filenames=['.halfapiconfig'])
PROJECT_NAME = config.get('project', 'name')

CONF_DIR = environ.get('HALFAPI_CONF_DIR', '/etc/halfapi')

config.read(filenames=[os.path.join(
    CONF_DIR,
    PROJECT_NAME 
)])

HOST = config.get('project', 'host')
PORT = config.getint('project', 'port')

DB_NAME = f'halfapi_{PROJECT_NAME}'
with open(config.get('project', 'secret')) as secret_file:
    SECRET = secret_file.read()

PRODUCTION = config.getboolean('project', 'production')
BASE_DIR = config.get('project', 'base_dir')

# DB
from half_orm.model import Model
db = Model(DB_NAME)
Domain = db.get_relation_class('api.domain')
APIRouter = db.get_relation_class('api.router')
APIRoute = db.get_relation_class('api.route')
AclFunction = db.get_relation_class('api.acl_function')
Acl = db.get_relation_class('api.acl')
RouteACL = db.get_relation_class('api.view.acl')

from halfapi.app import application
