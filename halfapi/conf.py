#!/usr/bin/env python3
import os
from os import environ
import sys
from configparser import ConfigParser

PROJECT_NAME = sys.argv.pop()
if len(PROJECT_NAME) == 0:
    raise Exception('Need a project name as argument')

config = ConfigParser(defaults={
    'project': {
        'host': '127.0.0.1',
        'port': '8000',
        'secret': None,
        'base_dir': None,
        'production': False
    }
})

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
