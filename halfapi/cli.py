#!/usr/bin/env python3
import click
import uvicorn
import os
import sys

CONTEXT_SETTINGS={
    'default_map':{'run': {'port': 8000}} 
}

@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None: 
        return run()

@click.option('--host', default='127.0.0.1')
@click.option('--port', default='8000')
@click.option('--debug', default=False)
@click.option('--dev', default=True)
@cli.command()
def run(host, port, debug, dev):
    if dev:
        debug = True
        reload = True
        log_level = 'debug'
    else:
        reload = False
        log_level = 'info'

    click.echo('Launching application with default parameters')
    click.echo(f'''Parameters : \n
    Host : {host}
    Port : {port}
    Debug : {debug}
    Dev : {dev}''')
    
    sys.path.insert(0, os.getcwd())
    click.echo(sys.path)
    uvicorn.run('halfapi.app:app', 
        host=host,
        port=int(port),
        log_level=log_level,
        reload=reload)

if __name__ == '__main__':
    cli()

