#!/usr/bin/env python3
"""
cli/init.py Defines the "halfapi init" cli commands

Helps the user to create a new project
"""
# builtins
import logging
import os
import sys
import re

import click

from .. import __version__
from ..conf import CONF_DIR

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
    """
    Returns the formatted template for /etc/half_api/PROJECT_NAME
    """
    return TMPL_HALFAPI_ETC.format(
        project=project,
        base_dir=path
    )

TMPL_HALFAPI_CONFIG = """[project]
name = {name}
halfapi_version = {halfapi_version}

[domains]
"""

@click.argument('project')
@cli.command()
def init(project):
    """
    The "halfapi init" command
    """
    if not re.match('^[a-z0-9_]+$', project, re.I):
        click.echo('Project name must match "^[a-z0-9_]+$", retry.', err=True)
        sys.exit(1)

    if os.path.exists(project):
        click.echo(f'A file named {project} already exists, abort.', err=True)
        sys.exit(1)


    logger.debug('Create directory %s', project)
    os.mkdir(project)

    logger.debug('Create directory %s/.halfapi', project)
    os.mkdir(f'{project}/.halfapi')

    with open(f'{project}/.halfapi/config', 'w') as conf_file:
        conf_file.write(TMPL_HALFAPI_CONFIG.format(
            name=project,
            halfapi_version=__version__))


    click.echo(f'Configure halfapi project in {CONF_DIR}/{project}')
    click.echo(format_halfapi_etc(project, CONF_DIR))
