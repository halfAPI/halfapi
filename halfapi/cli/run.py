import sys
import click
import uvicorn

from .cli import cli
from halfapi.cli.domain import list_routes
from halfapi.conf import (HOST, PORT,
    PRODUCTION, BASE_DIR, DOMAINS)

@click.option('--host', default=None)
@click.option('--port', default=None)
@cli.command()
def run(host, port):

    if not host:
        host = HOST

    if not port:
        port = PORT

    port = int(port)

    debug = reload = not PRODUCTION
    log_level = 'info' if PRODUCTION else 'debug'

    click.echo('Launching application')

    sys.path.insert(0, BASE_DIR)

    [ list_routes(domain) for domain in DOMAINS ]

    uvicorn.run('halfapi.app:application',
        host=host,
        port=int(port),
        log_level=log_level,
        reload=reload)
