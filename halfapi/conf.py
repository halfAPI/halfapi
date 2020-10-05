#!/usr/bin/env python3
"""
conf.py reads the current configuration files

It uses the following environment variables :

    - HALFAPI_CONF_DIR (default: /etc/half_api)


It defines the following globals :

    - PROJECT_NAME (str)
    - DOMAINS ([]) - seems to be unused except in this file
    - DOMAINSDICT ({domain_name: domain_module})
    - PRODUCTION (bool)
    - BASE_DIR (str)
    - HOST (str)
    - PORT (int)
    - CONF_DIR (str)
    - IS_PROJECT (bool)
    - config (ConfigParser)

It reads the following ressource :

    - ./.halfapi/config

It follows the following format :

    [project]
    name = PROJECT_NAME
    halfapi_version = HALFAPI_VERSION

    [domains]
    domain_name = requirements-like-url
"""

import logging
import os
from os import environ
import sys
from configparser import ConfigParser
import importlib

logger = logging.getLogger('halfapi')

PROJECT_NAME = ''
DOMAINS = []
DOMAINSDICT = {}
PRODUCTION = False
BASE_DIR = None
HOST = '127.0.0.1'
PORT = '3000'
CONF_DIR = environ.get('HALFAPI_CONF_DIR', '/etc/half_api')
SECRET = ''

IS_PROJECT = os.path.isfile('.halfapi/config')

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

if IS_PROJECT:
    config.read(filenames=['.halfapi/config'])

    PROJECT_NAME = config.get('project', 'name')

    if len(PROJECT_NAME) == 0:
        raise Exception('Need a project name as argument')

    DOMAINS = [domain for domain, _ in config.items('domains')] \
        if config.has_section('domains') \
        else []

    try:
        DOMAINSDICT = {
            dom: importlib.import_module(dom)
            for dom in DOMAINS
        }
    except ImportError as exc:
        logger.error('Could not load a domain : %s', exc)


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

    try:
        with open(config.get('project', 'secret')) as secret_file:
            SECRET = secret_file.read()
            # Set the secret so we can use it in domains
            os.environ['HALFAPI_SECRET'] = SECRET
    except FileNotFoundError as exc:
        logger.error('There is no file like %s : %s',
            config.get('project', 'secret'), exc)

    PRODUCTION = config.getboolean('project', 'production') or False
    os.environ['HALFAPI_PROD'] = str(PRODUCTION)

    BASE_DIR = config.get('project', 'base_dir')
