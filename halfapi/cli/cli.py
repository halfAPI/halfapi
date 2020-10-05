#!/usr/bin/env python3
"""
cli/cli.py Main entry point of halfapi cli tool

The init command is the only command loaded if not in a *project dir*, and it is
not loaded otherwise.
"""
# builtins
import click
from ..conf import IS_PROJECT

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
        return click.echo(version())

if IS_PROJECT:
    import halfapi.cli.config
    import halfapi.cli.domain
    import halfapi.cli.run

else:
    import halfapi.cli.init
