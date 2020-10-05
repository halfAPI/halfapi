#!/usr/bin/env python3
"""
cli/config.py Contains the .halfapi/config and HALFAPI_CONF_DIR/project_name templates

Defines the "halfapi config" command
"""
import click

from .cli import cli
from ..conf import (
    PROJECT_NAME,
    DOMAINS,
    HOST,
    PORT,
    PRODUCTION,
    BASE_DIR
)

CONF_STR=f"""
[project]
name = {PROJECT_NAME}
host = {HOST}
port = {PORT}
production = {PRODUCTION}
base_dir = {BASE_DIR}

[domains]"""

for dom in DOMAINS:
    CONF_STR = '\n'.join((CONF_STR, dom))

@cli.command()
def config():
    """
    Lists config parameters and their values
    """
    click.echo(CONF_STR)
