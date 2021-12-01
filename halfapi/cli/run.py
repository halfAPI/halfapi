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
from ..conf import (PROJECT_NAME, HOST, PORT, SCHEMA,
    PRODUCTION, LOGLEVEL, DOMAINSDICT, CONFIG, DOMAIN, ROUTER)
from ..logging import logger
from ..lib.schemas import schema_csv_dict

@click.option('--host', default=HOST)
@click.option('--port', default=PORT)
@click.option('--reload', default=False)
@click.option('--secret', default=False)
@click.option('--production', default=True)
@click.option('--loglevel', default=LOGLEVEL)
@click.option('--prefix', default='/')
@click.option('--check', default=True)
@click.argument('schema', type=click.File('r'), required=False)
@click.argument('router', required=False)
@click.argument('domain', required=False)
@cli.command()
def run(host, port, reload, secret, production, loglevel, prefix, check, schema, router, domain):
    """
    The "halfapi run" command
    """
    logger.debug('[run] host=%s port=%s reload=%s secret=%s production=%s loglevel=%s prefix=%s schema=%s',
        host, port, reload, secret, production, loglevel, prefix, schema
    )

    if not host:
        host = HOST

    if not port:
        port = PORT

    port = int(port)

    if PRODUCTION and reload:
        reload = False
        raise Exception('Can\'t use live code reload in production')

    log_level = LOGLEVEL or 'info'

    click.echo(f'Launching application {PROJECT_NAME}')

    CONFIG.get('domain')['name'] = domain
    CONFIG.get('domain')['router'] = router

    if schema:
        # Populate the SCHEMA global with the data from the given file
        for key, val in schema_csv_dict(schema, prefix).items():
            SCHEMA[key] = val

    # list_api_routes()

    click.echo(f'uvicorn.run("halfapi.app:application"\n' \
        f'host: {host}\n' \
        f'port: {port}\n' \
        f'log_level: {log_level}\n' \
        f'reload: {reload}\n'
    )

    uvicorn.run('halfapi.app:application',
        host=host,
        port=int(port),
        log_level=log_level,
        reload=reload)
