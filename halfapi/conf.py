#!/usr/bin/env python3
"""
conf.py reads the current configuration files

It uses the following environment variables :

    - HALFAPI_CONF_DIR (default: /etc/half_api)


It defines the following globals :

    - PROJECT_NAME (str) - HALFAPI_PROJECT_NAME
    - DOMAINSDICT ({domain_name: domain_module}) - HALFAPI_DOMAIN_NAME / HALFAPI_DOMAIN_MODULE
    - PRODUCTION (bool) - HALFAPI_PRODUCTION
    - LOGLEVEL (string) - HALFAPI_LOGLEVEL
    - BASE_DIR (str) - HALFAPI_BASE_DIR
    - HOST (str) - HALFAPI_HOST
    - PORT (int) - HALFAPI_PORT
    - CONF_DIR (str) - HALFAPI_CONF_DIR
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

from .lib.domain import d_domains

logger = logging.getLogger('uvicorn.asgi')

PROJECT_NAME = environ.get('HALFAPI_PROJECT_NAME') or os.path.basename(os.getcwd())
DOMAINSDICT = lambda: {}
DOMAINS = {}
PRODUCTION = False
LOGLEVEL = 'info'
HOST = '127.0.0.1'
PORT = '3000'
SECRET = ''
CONF_FILE = os.environ.get('HALFAPI_CONF_FILE', '.halfapi/config')

is_project = lambda: os.path.isfile(CONF_FILE)



default_config = {
    'project': {
        'host': '127.0.0.1',
        'port': '8000',
        'secret': '',
        'production': 'no'
    }
}

config = ConfigParser(allow_no_value=True)
config.read_dict(default_config)

CONF_DIR = environ.get('HALFAPI_CONF_DIR', '/etc/half_api')
HALFAPI_ETC_FILE=os.path.join(
    CONF_DIR, 'default.ini'
)

HALFAPI_DOT_FILE=os.path.join(
    os.getcwd(), '.halfapi', 'config')

HALFAPI_CONFIG_FILES = [ CONF_FILE, HALFAPI_DOT_FILE ]

def conf_files():
    return [
        os.path.join(
            CONF_DIR, 'default.ini'
        ),
        os.path.join(
            os.getcwd(), '.halfapi', 'config')]


def write_config():
    """
    Writes the current config to the highest priority config file
    """
    with open(conf_files()[-1], 'w') as halfapi_config:
        config.write(halfapi_config)

def config_dict():
    """
    The config object as a dict
    """
    return {
            section: dict(config.items(section))
            for section in config.sections()
    }

def read_config():
    """
    The highest index in "filenames" are the highest priorty
    """
    config.read(HALFAPI_CONFIG_FILES)



CONFIG = {}
read_config()

IS_PROJECT = True

PROJECT_NAME = config.get('project', 'name', fallback=PROJECT_NAME)

if len(PROJECT_NAME) == 0:
    raise Exception('Need a project name as argument')

DOMAINSDICT = lambda: d_domains(config)
DOMAINS = DOMAINSDICT()
if len(DOMAINS) == 0:
    logger.info('Domain-less instance')

HOST = config.get('project', 'host', fallback=environ.get('HALFAPI_HOST', '127.0.0.1'))
PORT = config.getint('project', 'port', fallback=environ.get('HALFAPI_PORT', '3000'))

try:
    with open(config.get('project', 'secret')) as secret_file:
        SECRET = secret_file.read().strip()
        CONFIG['secret'] = SECRET.strip()
        # Set the secret so we can use it in domains
        environ['HALFAPI_SECRET'] = SECRET
except FileNotFoundError as exc:
    if 'HALFAPI_SECRET' in environ:
        SECRET = environ.get('HALFAPI_SECRET')
        CONFIG['secret'] = SECRET.strip()
        # Set the secret so we can use it in domains
        environ['HALFAPI_SECRET'] = SECRET

    logger.error('There is no file like %s : %s',
        config.get('project', 'secret'), exc)

PRODUCTION = config.getboolean('project', 'production',
    fallback=environ.get('HALFAPI_PROD', False))

os.environ['HALFAPI_PROD'] = str(PRODUCTION)

LOGLEVEL = config.get('project', 'loglevel',
    fallback=environ.get('HALFAPI_LOGLEVEL', 'info')).lower()

BASE_DIR = config.get('project', 'base_dir',
    fallback=environ.get('HALFAPI_BASE_DIR', '.'))

CONFIG = {
    'project_name': PROJECT_NAME,
    'production': PRODUCTION,
    'secret': SECRET,
    'domains': DOMAINS,
    'domain_config': {}
}

for domain in DOMAINS:
    if domain not in config.sections():
        continue

    CONFIG['domain_config'][domain] = dict(config.items(domain))
