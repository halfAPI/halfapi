#!/usr/bin/env python3
"""
cli/routes.py Defines the "halfapi routes" cli commands
"""
# builtins
import sys
import importlib

import click

from .cli import cli

from ..lib.domain import gen_router_routes

@click.argument('module', required=True)
@click.option('--export', default=False, is_flag=True)
@cli.command()
def routes(module, export=False):
    """
    The "halfapi routes" command
    """
    try:
        mod = importlib.import_module(module)
    except ImportError as exc:
        raise click.BadParameter('Cannot import this module', param=module) from exc

    if export:
        for path, verb, m_router, fct, parameters in gen_router_routes(mod, []):
            for param in parameters:
                click.echo(';'.join((
                    path,
                    verb,
                    m_router.__name__,
                    fct.__name__,
                    param['acl'].__name__,
                    ','.join((param.get('in', [])))
                )))
