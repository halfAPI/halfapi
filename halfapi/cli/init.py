#!/usr/bin/env python3
"""
cli/init.py Defines the "halfapi init" cli commands

Helps the user to create a new project
"""
# builtins
import os
import sys
import re

import click

from .. import __version__
from ..conf import CONF_DIR

from .cli import cli

from ..logging import logger

TMPL_HALFAPI_ETC = """[project]
host = 127.0.0.1
port = 8000
secret = /path/to/secret_file
production = False
base_dir = {base_dir}
"""

TMPL_HALFAPI_CONFIG = """[project]
halfapi_version = {halfapi_version}

[domain]
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
            halfapi_version=__version__))


    click.echo(f'Configure halfapi project in {CONF_DIR}/{project}')
