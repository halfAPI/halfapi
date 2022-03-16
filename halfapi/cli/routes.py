#!/usr/bin/env python3
"""
cli/routes.py Defines the "halfapi routes" cli commands
"""
# builtins
import sys
import importlib
from pprint import pprint
import orjson

import click

from .cli import cli

from ..logging import logger

# from ..lib.domain import domain_schema_dict
from ..lib.constants import DOMAIN_SCHEMA, ROUTE_SCHEMA
from ..lib.responses import ORJSONResponse

@click.argument('module', required=True)
@click.option('--export', default=False, is_flag=True)
@click.option('--validate', default=False, is_flag=True)
@click.option('--check', default=False, is_flag=True)
@click.option('--noheader', default=False, is_flag=True)
@click.option('--schema', default=False, is_flag=True)
@cli.command()
def routes(module, export=False, validate=False, check=False, noheader=False, schema=False):
    """
    The "halfapi routes" command
    """
    # try:
    #     mod = importlib.import_module(module)
    # except ImportError as exc:
    #     raise click.BadParameter('Cannot import this module', param=module) from exc

    # if export:
    #     click.echo(schema_to_csv(module, header=not noheader))

    # if schema:
    #     routes_d = domain_schema_dict(mod)
    #     ROUTE_SCHEMA.validate(routes_d)
    #     click.echo(orjson.dumps(routes_d,
    #         option=orjson.OPT_NON_STR_KEYS,
    #         default=ORJSONResponse.default_cast))


    # if validate:
    #     routes_d = domain_schema_dict(mod)
    #     try:
    #         ROUTE_SCHEMA.validate(routes_d)
    #     except Exception as exc:
    #         raise exc

