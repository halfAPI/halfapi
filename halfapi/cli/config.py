#!/usr/bin/env python3
import click

from .cli import cli
from halfapi.conf import (
    PROJECT_NAME,
    DOMAINS,
    CONF_DIR,
    HOST,
    PORT,
    DB_NAME,
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
