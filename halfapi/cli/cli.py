#!/usr/bin/env python3
"""
cli/cli.py Main entry point of halfapi cli tool

The init command is the only command loaded if not in a *project dir*, and it is
not loaded otherwise.
"""
# builtins
import click
from ..conf import IS_PROJECT, IS_HOP_PROJECT

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True)
@click.pass_context
def cli(ctx, version):
    """
    HalfAPI Cli entry point

    It uses the Click library
    """
    if version:
        from halfapi import version
        click.echo(version())

if IS_PROJECT:
    from . import config
    from . import domain
    from . import run
elif IS_HOP_PROJECT:
    from . import init_hop
    from . import route
else:
    from . import init
