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
from ..conf import (PROJECT_NAME, HOST, PORT,
    PRODUCTION, LOGLEVEL, DOMAINSDICT)

@click.option('--host', default=None)
@click.option('--port', default=None)
@click.option('--reload', default=False)
@cli.command()
def run(host, port, reload):
    """
    The "halfapi run" command
    """

    if not host:
        host = HOST

    if not port:
        port = PORT

    port = int(port)

    if PRODUCTION:
        reload = False
        raise Exception('Can\'t use live code reload in production')

    log_level = 'info' if PRODUCTION else LOGLEVEL

    click.echo(f'Launching application {PROJECT_NAME}')

    sys.path.insert(0, os.getcwd())

    list_api_routes()

    uvicorn.run('halfapi.app:application',
        host=host,
        port=int(port),
        log_level=log_level,
        reload=reload)
