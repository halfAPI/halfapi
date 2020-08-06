#!/usr/bin/env python3
import os
from os import environ
import sys
from configparser import ConfigParser

IS_PROJECT = os.path.isfile('.halfapi/config')

if IS_PROJECT:

    default_config = {
        'project': {
            'host': '127.0.0.1',
            'port': '8000',
            'secret': '',
            'base_dir': '',
            'production': 'no'
        }
    }

    config = ConfigParser(allow_no_value=True)
    config.read_dict(default_config)
    config.read(filenames=['.halfapi/config'])

    PROJECT_NAME = config.get('project', 'name')

    if len(PROJECT_NAME) == 0:
        raise Exception('Need a project name as argument')

    DOMAINS = [domain for domain, _ in config.items('domains')]

    CONF_DIR = environ.get('HALFAPI_CONF_DIR', '/etc/half_api')

    HALFAPI_CONF_FILE=os.path.join(
        CONF_DIR,
        PROJECT_NAME
    )
    if not os.path.isfile(HALFAPI_CONF_FILE):
        print(f'Missing {HALFAPI_CONF_FILE}, exiting')
        sys.exit(1)
    config.read(filenames=[HALFAPI_CONF_FILE])

    HOST = config.get('project', 'host')
    PORT = config.getint('project', 'port')
    DB_NAME = f'halfapi_{PROJECT_NAME}'

    try:
        with open(config.get('project', 'secret')) as secret_file:
            SECRET = secret_file.read()
    except FileNotFoundError:
        print('There is no file like {}'.format(config.get('project', 'secret')))
        sys.exit(1)

    PRODUCTION = config.getboolean('project', 'production')
    BASE_DIR = config.get('project', 'base_dir')
