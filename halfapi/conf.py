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

import logging
import os
from os import environ
import sys
import importlib
import tempfile
import uuid

import toml

from .logging import logger

PRODUCTION = True
LOGLEVEL = 'info'
CONF_FILE = os.environ.get('HALFAPI_CONF_FILE', '.halfapi/config')
DRYRUN = bool(os.environ.get('HALFAPI_DRYRUN', False))

SCHEMA = {}

CONF_DIR = environ.get('HALFAPI_CONF_DIR', '/etc/half_api')
HALFAPI_ETC_FILE=os.path.join(
    CONF_DIR, 'config'
)
HALFAPI_DOT_FILE=os.path.join(
    os.getcwd(), '.halfapi', 'config')

HALFAPI_CONFIG_FILES = []

try:
    with open(HALFAPI_ETC_FILE, 'r'):
        HALFAPI_CONFIG_FILES.append(HALFAPI_ETC_FILE)
except FileNotFoundError:
    logger.error('Cannot find a configuration file under %s', HALFAPI_DOT_FILE)

try:
    with open(HALFAPI_DOT_FILE, 'r'):
        HALFAPI_CONFIG_FILES.append(HALFAPI_DOT_FILE)
except FileNotFoundError:
    logger.error('Cannot find a configuration file under %s', HALFAPI_DOT_FILE)


def read_config():
    """
    The highest index in "filenames" are the highest priorty
    """
    d_res = {}

    logger.info('Reading config files %s', HALFAPI_CONFIG_FILES)
    for CONF_FILE in HALFAPI_CONFIG_FILES:
        d_res.update( toml.load(HALFAPI_CONFIG_FILES) )

    logger.info('Reading config files (result) %s', d_res)
    return { **d_res.get('project', {}), 'domain': d_res.get('domain', {}) }

CONFIG = read_config()

PROJECT_NAME = CONFIG.get('project_name',
    environ.get('HALFAPI_PROJECT_NAME', os.getcwd().split('/')[-1]))

if environ.get('HALFAPI_DOMAIN_NAME'):
    DOMAIN_NAME = environ.get('HALFAPI_DOMAIN_NAME')
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

    if environ.get('HALFAPI_DOMAIN_MODULE'):
        dom_module = environ.get('HALFAPI_DOMAIN_MODULE')
        CONFIG['domain'][DOMAIN_NAME]['module'] = dom_module

if len(CONFIG.get('domain', {}).keys()) == 0:
    logger.info('No domains')

# Bind
HOST = CONFIG.get('host',
    environ.get('HALFAPI_HOST', '127.0.0.1'))
PORT = int(CONFIG.get(
    'port',
    environ.get('HALFAPI_PORT', '3000')))


# Secret
SECRET = CONFIG.get(
    'secret',
    environ.get('HALFAPI_SECRET'))

if not SECRET:
    # TODO: Create a temporary secret
    _, SECRET = tempfile.mkstemp()
    with open(SECRET, 'w') as secret_file:
        secret_file.write(str(uuid.uuid4()))

try:
    with open(SECRET, 'r') as secret_file:
        CONFIG['secret'] = SECRET.strip()
except FileNotFoundError as exc:
    logger.info('Running without secret file: %s', SECRET or 'no file specified')

PRODUCTION = bool(CONFIG.get(
    'production',
    environ.get('HALFAPI_PROD', True)))

LOGLEVEL = CONFIG.get(
    'loglevel',
    environ.get('HALFAPI_LOGLEVEL', 'info')).lower()

BASE_DIR = CONFIG.get(
    'base_dir',
    environ.get('HALFAPI_BASE_DIR', '.'))

CONFIG['project_name'] = PROJECT_NAME
CONFIG['production'] = PRODUCTION
CONFIG['secret'] = SECRET
CONFIG['host'] = HOST
CONFIG['port'] = PORT
CONFIG['dryrun'] = DRYRUN
