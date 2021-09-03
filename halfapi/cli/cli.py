#!/usr/bin/env python3
"""
cli/cli.py Main entry point of halfapi cli tool

The init command is the only command loaded if not in a *project dir*, and it is
not loaded otherwise.
"""
# builtins
import click

IS_PROJECT = True
try:
    from ..conf import DOMAINS
except Exception:
    IS_PROJECT = False

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

else:
    from . import init
