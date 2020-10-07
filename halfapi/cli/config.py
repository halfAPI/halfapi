#!/usr/bin/env python3
"""
cli/config.py Contains the .halfapi/config and HALFAPI_CONF_DIR/project_name templates

Defines the "halfapi config" command
"""
import click

from .cli import cli
from ..conf import (
    read_config,
    PROJECT_NAME,
    DOMAINSDICT,
    HOST,
    PORT,
    PRODUCTION,
)

CONF_STR=f"""
[project]
name = {PROJECT_NAME}
host = {HOST}
port = {PORT}
production = {PRODUCTION}

[domains]"""

for dom in DOMAINSDICT():
    CONF_STR = '\n'.join((CONF_STR, dom))


@cli.command()
def config():
    """
    Lists config parameters and their values
    """
    click.echo(read_config())
