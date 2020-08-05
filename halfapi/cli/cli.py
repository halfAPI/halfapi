#!/usr/bin/env python3
# builtins
import click
from halfapi.conf import IS_PROJECT

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True)
@click.pass_context
def cli(ctx, version):
    if version:
        import halfapi
        return click.echo(halfapi.version)
     
    #if not IS_PROJECT:
    #    return init()
    #if ctx.invoked_subcommand is None: 
    #    return run()

if IS_PROJECT:
    import halfapi.cli.domain
    import halfapi.cli.run
else:
    import halfapi.cli.init
