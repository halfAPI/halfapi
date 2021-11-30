#!/usr/bin/env python3
"""
cli/routes.py Defines the "halfapi routes" cli commands
"""
# builtins
import sys
import importlib
from pprint import pprint

import click

from .cli import cli

from ..logging import logger

from ..lib.domain import gen_router_routes
from ..lib.constants import DOMAIN_SCHEMA
from ..lib.routes import api_routes
from ..lib.schemas import schema_to_csv

@click.argument('module', required=True)
@click.option('--export', default=False, is_flag=True)
@click.option('--validate', default=False, is_flag=True)
@click.option('--check', default=False, is_flag=True)
@click.option('--noheader', default=False, is_flag=True)
@cli.command()
def routes(module, export=False, validate=False, check=False, noheader=False):
    """
    The "halfapi routes" command
    """
    try:
        mod = importlib.import_module(module)
    except ImportError as exc:
        raise click.BadParameter('Cannot import this module', param=module) from exc

    if export:
        click.echo(schema_to_csv(module, header=not noheader))

    if validate:
        routes_d = api_routes(mod)
        try:
            DOMAIN_SCHEMA.validate(routes_d[0])
        except Exception as exc:
            pprint(routes_d[0])
            raise exc from exc
