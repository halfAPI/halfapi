#!/usr/bin/env python3
# builtins
import click

@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.option('--version', is_flag=True)
@click.pass_context
def cli(ctx, version):
    if version:
        import halfapi
        return click.echo(halfapi.version)

    if ctx.invoked_subcommand is None: 
        return run()

if __name__ == '__main__':
    cli()
