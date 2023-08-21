#!/usr/bin/env python3
"""
conf.py reads the current configuration files

It uses the following environment variables :

    - HALFAPI_CONF_DIR (default: /etc/half_api)


It defines the following globals :

    - PROJECT_NAME (str) - HALFAPI_PROJECT_NAME
    - PRODUCTION (bool) - HALFAPI_PRODUCTION
    - LOGLEVEL (str) - HALFAPI_LOGLEVEL
    - BASE_DIR (str) - HALFAPI_BASE_DIR
    - HOST (str) - HALFAPI_HOST
    - PORT (int) - HALFAPI_PORT
    - CONF_DIR (str) - HALFAPI_CONF_DIR
    - DRYRUN (bool) - HALFAPI_DRYRUN

It reads the following ressource :

    - ./.halfapi/config

It follows the following format :

    [project]
    halfapi_version = HALFAPI_VERSION

    [domain.domain_name]
    name = domain_name
    routers = routers

    [domain.domain_name.config]
    option = Argh

"""

from .logging import logger
import os
from os import environ
import sys
import importlib
import tempfile
import uuid

import toml

SCHEMA = {}

DEFAULT_CONF = {
    # Default configuration values
    'SECRET': tempfile.mkstemp()[1],
    'PROJECT_NAME': os.getcwd().split('/')[-1],
    'PRODUCTION': True,
    'HOST': '127.0.0.1',
    'PORT': 3000,
    'LOGLEVEL': 'info',
    'BASE_DIR': os.getcwd(),
    'CONF_FILE': '.halfapi/config',
    'CONF_DIR': '/etc/half_api',
    'DRYRUN': None
}

PROJECT_LEVEL_KEYS = {
    # Allowed keys in "project" section of configuration file
    'project_name',
    'production',
    'secret',
    'host',
    'port',
    'loglevel',
    'dryrun'
}

DOMAIN_LEVEL_KEYS = PROJECT_LEVEL_KEYS | {
    # Allowed keys in "domain" section of configuration file
    'name',
    'module',
    'prefix',
    'enabled'
}

CONF_FILE = os.environ.get('HALFAPI_CONF_FILE', DEFAULT_CONF['CONF_FILE'])
CONF_DIR = os.environ.get('HALFAPI_CONF_DIR', DEFAULT_CONF['CONF_DIR'])

HALFAPI_ETC_FILE=os.path.join(
    CONF_DIR, 'config'
)

BASE_DIR = os.environ.get('HALFAPI_BASE_DIR', DEFAULT_CONF['BASE_DIR'])
HALFAPI_DOT_FILE=os.path.join(
    BASE_DIR, '.halfapi', 'config')

HALFAPI_CONFIG_FILES = []

try:
    with open(HALFAPI_ETC_FILE, 'r'):
        HALFAPI_CONFIG_FILES.append(HALFAPI_ETC_FILE)
except FileNotFoundError:
    logger.info('Cannot find a configuration file under %s', HALFAPI_ETC_FILE)

try:
    with open(HALFAPI_DOT_FILE, 'r'):
        HALFAPI_CONFIG_FILES.append(HALFAPI_DOT_FILE)
except FileNotFoundError:
    logger.info('Cannot find a configuration file under %s', HALFAPI_DOT_FILE)


ENVIRONMENT = {}
# Load environment variables allowed in configuration

if 'HALFAPI_DRYRUN' in os.environ:
    ENVIRONMENT['dryrun'] = True

if 'HALFAPI_PROD' in os.environ:
    ENVIRONMENT['production'] = bool(os.environ.get('HALFAPI_PROD'))

if 'HALFAPI_LOGLEVEL' in os.environ:
    ENVIRONMENT['loglevel'] = os.environ.get('HALFAPI_LOGLEVEL').lower()

if 'HALFAPI_SECRET' in os.environ:
    ENVIRONMENT['secret'] = os.environ.get('HALFAPI_SECRET')

if 'HALFAPI_HOST' in os.environ:
    ENVIRONMENT['host'] = os.environ.get('HALFAPI_HOST')

if 'HALFAPI_PORT' in os.environ:
    ENVIRONMENT['port'] = int(os.environ.get('HALFAPI_PORT'))

def read_config(filenames=HALFAPI_CONFIG_FILES):
    """
    The highest index in "filenames" are the highest priorty
    """
    d_res = {}

    logger.info('Reading config files %s', filenames)
    for CONF_FILE in filenames:
        if os.path.isfile(CONF_FILE):
            conf_dict = toml.load(CONF_FILE)
            d_res.update(conf_dict)

    logger.info('Read config files (result) %s', d_res)
    return { **d_res.get('project', {}), 'domain': d_res.get('domain', {}) }

CONFIG = read_config()
CONFIG.update(**ENVIRONMENT)

PROJECT_NAME = CONFIG.get('project_name',
    os.environ.get('HALFAPI_PROJECT_NAME', DEFAULT_CONF['PROJECT_NAME']))

if os.environ.get('HALFAPI_DOMAIN_NAME'):
    # Force enabled domain by environment variable

    DOMAIN_NAME = os.environ.get('HALFAPI_DOMAIN_NAME')
    if 'domain' in CONFIG and DOMAIN_NAME in CONFIG['domain'] \
        and 'config' in CONFIG['domain'][DOMAIN_NAME]:

        domain_config = CONFIG['domain'][DOMAIN_NAME]['config']
    else:
        domain_config = {}

    CONFIG['domain'] = {}

    CONFIG['domain'][DOMAIN_NAME] = {
        'enabled': True,
        'name': DOMAIN_NAME,
        'prefix': False
    }

    CONFIG['domain'][DOMAIN_NAME]['config'] = domain_config

    if os.environ.get('HALFAPI_DOMAIN_MODULE'):
        # Specify the pythonpath to import the specified domain (defaults to global)
        dom_module = os.environ.get('HALFAPI_DOMAIN_MODULE')
        CONFIG['domain'][DOMAIN_NAME]['module'] = dom_module

if len(CONFIG.get('domain', {}).keys()) == 0:
    logger.info('No domains')


# Secret
if 'secret' not in CONFIG:
    # TODO: Create a temporary secret
    CONFIG['secret'] = DEFAULT_CONF['SECRET']
    with open(CONFIG['secret'], 'w') as secret_file:
        secret_file.write(str(uuid.uuid4()))

try:
    with open(CONFIG['secret'], 'r') as secret_file:
        CONFIG['secret'] = CONFIG['secret'].strip()
except FileNotFoundError as exc:
    logger.warning('Running without secret file: %s', CONFIG['secret'] or 'no file specified')

CONFIG.setdefault('project_name', DEFAULT_CONF['PROJECT_NAME'])
CONFIG.setdefault('production', DEFAULT_CONF['PRODUCTION'])
CONFIG.setdefault('host', DEFAULT_CONF['HOST'])
CONFIG.setdefault('port', DEFAULT_CONF['PORT'])
CONFIG.setdefault('loglevel', DEFAULT_CONF['LOGLEVEL'])
CONFIG.setdefault('dryrun', DEFAULT_CONF['DRYRUN'])

# !!!TO REMOVE!!!
SECRET = CONFIG.get('secret')
PRODUCTION = CONFIG.get('production')
# !!!
