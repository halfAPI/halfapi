#!/usr/bin/env python3
"""
cli/config.py Contains the .halfapi/config and HALFAPI_CONF_DIR/project_name templates

Defines the "halfapi config" command
"""
import click

from .cli import cli
from ..conf import CONFIG

CONF_STR="""
[project]
name = {project_name}
host = {host}
port = {port}
production = {production}

[domain]
name = {domain_name}
router = {router}
"""


@cli.command()
def config():
    """
    Lists config parameters and their values
    """
    click.echo(CONF_STR)
