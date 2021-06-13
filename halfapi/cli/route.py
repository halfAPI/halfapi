import os
import sys
from configparser import ConfigParser
import importlib
import click

from half_orm.model import Model

from .cli import cli
from halfapi.lib.domain import VERBS


def get_package_module(name):
    hop_conf_path = os.path.join('.hop', 'config')
    config = ConfigParser()
    config.read([ hop_conf_path ])

    assert os.path.isdir(config.get('halfORM', 'package_name'))
    package_name = config.get('halfORM', 'package_name')

    if sys.path[0] != '.':
        sys.path.insert(0, '.')

    module = importlib.import_module(
        '.'.join((
            package_name,
            'halfapi',
            name)))

    if not module:
        raise Exception('Could not import {}. Please hop update -f'.format(
            '.'.join((
                config.get('halfORM', 'package_name'),
                'halfapi',
                name))))

    return module

@cli.group()
def route():
    pass
    
def endpoint_create(verb, endpoint, endpoint_type):
    Endpoint_mod = get_package_module('endpoint')
    Endpoint = Endpoint_mod.Endpoint
    EndpointTypeDoesNotExist =  Endpoint_mod.EndpointTypeDoesNotExist

    try:
        click.echo('Endpoint creation')
        new_endpoint = Endpoint.create(
            verb=verb, endpoint=endpoint, endpoint_type=endpoint_type
        )
        return Endpoint(**new_endpoint).path
    except EndpointTypeDoesNotExist:
        create_endpoint_type = click.prompt(
            'The endpoint type {} does not exist. Do you want to create it?'.format(endpoint_type),
            default='n',
            type=click.Choice(['y', 'N'], case_sensitive=False)
        )
        if create_endpoint_type.lower() == 'n':
            click.echo('Aborting...')
            sys.exit(0)

        EndpointType_mod = get_package_module('endpoint_type')
        EndpointType = EndpointType_mod.EndpointType
        EndpointType.create(endpoint_type)

        return endpoint_create(package_name, verb, endpoint, endpoint_type)

        
@click.option('--type', prompt=True, type=str, default='JSON')
@click.option('--endpoint', prompt=True, type=str)
@click.option('--verb', prompt=True, type=click.Choice(VERBS, case_sensitive=False))
@route.command()
def add(verb, endpoint, type):
    """
    The "halfapi route add" command for hop projects
    """
    click.echo('About to create a new route : [{}] {} -> {}'.format(verb, endpoint, type))
    new_endpoint = endpoint_create(verb, endpoint, type)
    click.echo(f'Created endpoint {new_endpoint}')


@route.command()
def list():
    """
    The "halfapi route list" command for hop projects
    """
    Endpoint_mod = get_package_module('endpoint')
    Endpoint = Endpoint_mod.Endpoint

    click.echo('Current routes :')
    for endpoint in Endpoint().select():
        elt = Endpoint(**endpoint)
        click.echo(f'{elt.method}: {elt.path}')
