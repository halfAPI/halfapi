#!/usr/bin/env python3
"""
cli/domain.py Defines the "halfapi domain" cli commands
"""
# builtins
import os
import sys
import importlib
import subprocess

import json
import toml

import click
import orjson
import uvicorn


from .cli import cli
from ..conf import CONFIG

from ..half_domain import HalfDomain

from ..lib.routes import api_routes
from ..lib.responses import ORJSONResponse
from ..conf import CONFIG, PROJECT_LEVEL_KEYS


from ..logging import logger

#################
# domain create #
#################
def create_domain(domain_name: str, module_path: str):
    logger.info('Will add **%s** (%s) to current halfAPI project',
            domain_name, module_path)

    #if domain_name in DOMAINSDICT():
    #    logger.warning('Domain **%s** is already in project', domain_name)
    #    sys.exit(1)

    def domain_tree_create():
        def create_init(path):
            with open(os.path.join(os.getcwd(), path, '__init__.py'), 'w') as f:
                f.writelines([
                    '"""',
                    f'name: {domain_name}',
                    f'router: {module_path}',
                    '"""'
                ])
                logger.debug('created %s', os.path.join(os.getcwd(), path, '__init__.py'))

        def create_acl(path):
            with open(os.path.join(path, 'acl.py'), 'w') as f:
                f.writelines([
                    'from halfapi.lib.acl import public, ACLS',

                ])
                logger.debug('created %s', os.path.join(path, 'acl.py'))


        os.mkdir(domain_name)
        create_init(domain_name)
        router_path = os.path.join(domain_name, 'routers')
        create_acl(domain_name)
        os.mkdir(router_path)
        create_init(router_path)

    # TODO: Generate config file

    domain_tree_create()
    """
    try:
        importlib.import_module(module_path)
    except ImportError:
        logger.error('cannot import %s', domain_name)
        domain_tree_create()
    """

    """
    try:
        importlib.import_module(domain_name)
    except ImportError:
        click.echo('Error in domain creation')
        logger.debug('%s', subprocess.run(['tree', 'a', os.getcwd()]))
        raise Exception('cannot create domain {}'.format(domain_name))
    """



###############
# domain read #
###############
def list_routes(domain, m_dom):
    """
    Echoes the list of the **m_dom** active routes
    """

    click.echo(f'\nDomain : {domain}\n')

    routes = api_routes(m_dom)[0]
    if len(routes):
        for key, item in routes.items():
            methods = '|'.join(list(item.keys()))
            click.echo(f'\t{key} : {methods}')
    else:
        click.echo('\t**No ROUTES**')
        raise Exception('Routeless domain')



def list_api_routes():
    """
    Echoes the list of all active domains.

    TODO: Rewrite function
    """

    click.echo('# API Routes')
    # for domain, m_dom in DOMAINSDICT().items():
    #     list_routes(domain, m_dom)


@click.option('--devel',default=None, is_flag=True)
@click.option('--watch',default=False, is_flag=True)
@click.option('--production',default=None, is_flag=True)
@click.option('--port',default=None, type=int)
@click.option('--log-level',default=None, type=str)
@click.option('--dry-run',default=False, is_flag=True)
@click.option('--run',default=False, is_flag=True)
@click.option('--read',default=False, is_flag=True)
@click.option('--conftest',default=False, is_flag=True)
@click.option('--create',default=False, is_flag=True)
@click.option('--update',default=False, is_flag=True)
@click.option('--delete',default=False, is_flag=True)
@click.argument('config_file', type=click.File(mode='rb'), required=False)
@click.argument('domain',default=None, required=False)
@cli.command()
def domain(domain, config_file, delete, update, create, conftest, read, run, dry_run, log_level, port, production, watch, devel):
    """
    The "halfapi domain" command

    Parameters:
        domain (str|None): The domain name

        The parameter has a misleading name as it is a multiple option
        but this would be strange to use it several times named as "domains"

        update (boolean): If set, update the database for the selected domains
    """
    if not domain:
        if create:
            # TODO: Connect to the create_domain function
            raise NotImplementedError
        raise Exception('Missing domain name')

    if config_file:
        ARG_CONFIG = toml.load(config_file.name)
            
        if 'project' in ARG_CONFIG:
            for key, value in ARG_CONFIG['project'].items():
                if key in PROJECT_LEVEL_KEYS:
                    CONFIG[key] = value

        if 'domain' in ARG_CONFIG and domain in ARG_CONFIG['domain']:
            for key, value in ARG_CONFIG['domain'][domain].items():
                if key in PROJECT_LEVEL_KEYS:
                    CONFIG[key] = value

        CONFIG['domain'].update(ARG_CONFIG['domain'])

    if create:
        raise NotImplementedError
    elif update:
        raise NotImplementedError
    elif delete:
        raise NotImplementedError
    elif read:
        from ..halfapi import HalfAPI

        halfapi = HalfAPI(CONFIG)
        click.echo(orjson.dumps(
            halfapi.domains[domain].schema(),
            option=orjson.OPT_NON_STR_KEYS,
            default=ORJSONResponse.default_cast)
        )

    else:
        if dry_run:
            CONFIG['dryrun'] = True

        domains = CONFIG.get('domain')
        for key in domains.keys():
            if key != domain:
                domains[key]['enabled'] = False
            else:
                domains[key]['enabled'] = True

        if not log_level:
            log_level = CONFIG.get('domain', {}).get('loglevel', CONFIG.get('loglevel', False))
        else:
            CONFIG['loglevel'] = log_level

        if not port:
            port = CONFIG.get('domain', {}).get('port', CONFIG.get('port', False))
        else:
            CONFIG['port'] = port

        if devel is None and production is not None and (production is False or production is True):
            CONFIG['production'] = production

        if devel is not None:
            CONFIG['production'] = False
            CONFIG['loglevel'] = 'debug'


        if conftest:
            click.echo(
                toml.dumps(CONFIG)
            )

        else:
            # domain section port is preferred, if it doesn't exist we use the global one

            uvicorn_kwargs = {}

            if CONFIG.get('port'):
                uvicorn_kwargs['port'] = CONFIG['port']

            if CONFIG.get('loglevel'):
                uvicorn_kwargs['log_level'] = CONFIG['loglevel'].lower()

            if watch:
                uvicorn_kwargs['reload'] = True

            uvicorn.run(
                'halfapi.app:application',
                factory=True,
                **uvicorn_kwargs
            )

    sys.exit(0)
