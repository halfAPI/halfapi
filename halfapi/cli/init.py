#!/usr/bin/env python3
# builtins
import os
import sys
import re
import click
import logging

from halfapi import __version__
from .cli import cli

logger = logging.getLogger('halfapi')

TMPL_HALFAPI_ETC = """[project]
name = {project}
host = 127.0.0.1 
port = 8000
secret = /path/to/secret_file
production = False
base_dir = {base_dir}
"""

def format_halfapi_etc(project, path):
    return TMPL_HALFAPI_ETC.format(
        project=project,
        base_dir=path
    )

TMPL_HALFAPI_CONFIG = """[project]
name = {name}
halfapi_version = {halfapi_version}
"""

@click.argument('project')
@click.option('--venv', default=None)
@cli.command()
def init(project, venv):
    if not re.match('^[a-z0-9_]+$', project, re.I):
        click.echo('Project name must match "^[a-z0-9_]+$", retry.', err=True)
        sys.exit(1)

    if os.path.exists(project):
        click.echo(f'A file named {project} already exists, abort.', err=True)
        sys.exit(1)


    click.echo(f'create directory {project}')
    os.mkdir(project)
