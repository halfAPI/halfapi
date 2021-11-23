#!/usr/bin/env python3
"""
cli/config.py Contains the .halfapi/config and HALFAPI_CONF_DIR/project_name templates

Defines the "halfapi config" command
"""
import click

from .cli import cli
from ..conf import CONFIG

DOMAINS_STR='\n'.join(
    [ ' = '.join((key, val.__name__)) for key, val in CONFIG['domains'].items() ]
)

CONF_STR="""
[project]
name = {project_name}
host = {host}
port = {port}
production = {production}

[domains]
""".format(**CONFIG) + DOMAINS_STR

@cli.command()
def config():
    """
    Lists config parameters and their values
    """
    click.echo(CONF_STR)
