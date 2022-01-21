#!/usr/bin/env python3
"""
cli/domain.py Defines the "halfapi run" cli command
"""
import os
import sys
import click
import uvicorn

from .cli import cli
from .domain import list_api_routes
from ..conf import CONFIG, SCHEMA
from ..logging import logger
from ..lib.schemas import schema_csv_dict
from ..half_domain import HalfDomain

@click.option('--host', default=CONFIG.get('host'))
@click.option('--port', default=CONFIG.get('port'))
@click.option('--reload', default=False)
@click.option('--secret', default=CONFIG.get('secret'))
@click.option('--production', default=CONFIG.get('secret'))
@click.option('--loglevel', default=CONFIG.get('loglevel'))
@click.option('--prefix', default='/')
@click.option('--check', default=True)
@click.option('--dryrun', default=False, is_flag=True)
@click.argument('schema', type=click.File('r'), required=False)
@click.argument('domain', required=False)
@cli.command()
def run(host, port, reload, secret, production, loglevel, prefix, check, dryrun,
        schema, domain):
    """
    The "halfapi run" command
    """
    logger.debug('[run] host=%s port=%s reload=%s secret=%s production=%s loglevel=%s prefix=%s schema=%s',
        host, port, reload, secret, production, loglevel, prefix, schema
    )

    port = int(port)

    if production and reload:
        reload = False
        raise Exception('Can\'t use live code reload in production')

    click.echo(f'Launching application')

    if secret:
        CONFIG['secret'] = secret

    if schema:
        # Populate the SCHEMA global with the data from the given file
        for key, val in schema_csv_dict(schema, prefix).items():
            SCHEMA[key] = val

    if domain:
        # If we specify a domain to run as argument
        if 'domain' not in CONFIG:
            CONFIG['domain'] = {}

        # Disable all domains
        keys = list(CONFIG.get('domain').keys())
        for key in keys:
            CONFIG['domain'].pop(key)

        # And activate the desired one, mounted without prefix
        CONFIG['domain'][domain] = {
            'name': domain,
            'prefix': False,
            'enabled': True
        }

    # list_api_routes()

    click.echo(f'uvicorn.run("halfapi.app:application"\n' \
        f'host: {host}\n' \
        f'port: {port}\n' \
        f'log_level: {loglevel}\n' \
        f'reload: {reload}\n'
    )

    if dryrun:
        CONFIG['dryrun'] = True

    uvicorn.run('halfapi.app:application',
        host=host,
        port=int(port),
        log_level=loglevel,
        reload=reload)
