#!/usr/bin/env python3
"""
cli/domain.py Defines the "halfapi run" cli command
"""
import sys
import click
import uvicorn

from .cli import cli
from .domain import list_api_routes
from ..conf import (PROJECT_NAME, HOST, PORT,
    PRODUCTION, BASE_DIR, DOMAINSDICT)

@click.option('--host', default=None)
@click.option('--port', default=None)
@cli.command()
def run(host, port):
    """
    The "halfapi run" command
    """

    if not host:
        host = HOST

    if not port:
        port = PORT

    port = int(port)

    reload = not PRODUCTION
    log_level = 'info' if PRODUCTION else 'debug'

    click.echo(f'Launching application {PROJECT_NAME}')

    sys.path.insert(0, BASE_DIR)

    list_api_routes()

    uvicorn.run('halfapi.app:application',
        host=host,
        port=int(port),
        log_level=log_level,
        reload=reload)
