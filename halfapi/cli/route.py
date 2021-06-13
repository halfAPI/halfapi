import os
import sys
from configparser import ConfigParser
import importlib
import click

from half_orm.model import Model

from .cli import cli
from halfapi.lib.domain import VERBS

def get_package_name():
    hop_conf_path = os.path.join('.hop', 'config')
    config = ConfigParser()
    config.read([ hop_conf_path ])

    assert os.path.isdir(config.get('halfORM', 'package_name'))
    return config.get('halfORM', 'package_name')


def get_package_module(name):
    package_name = get_package_name()

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

        return endpoint_create(verb, endpoint, endpoint_type)

        
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


@click.option('--target', default='./Lib/api', type=str)
@route.command()
def update(target):
    """
    The "halfapi route update" command for hop projects

    Creates the router tree under <target>, and add missing methods
    for endpoints, that raise NotImplementedError
    """
    from time import sleep

    package = get_package_name()
    target_path = os.path.join(os.path.abspath('.'), package, target)

    if not os.path.isdir(target_path):
        raise Exception('Missing target path {}'.format(target_path))

    click.echo('Will create router tree in {}'.format(target_path))
    proceed = click.prompt(
        'Proceed? [Y/n]',
        default='y',
        type=click.Choice(['Y', 'n'], case_sensitive=False)
    )

    if proceed.lower() == 'n':
        sys.exit()

    Endpoint_mod = get_package_module('endpoint')
    Endpoint = Endpoint_mod.Endpoint

    missing_methods = {}

    for endpoint in Endpoint().select():
        elt = Endpoint(**endpoint)
        path = elt.path
        stack = [target_path]

        for segment in path.split('/'):
            stack.append(segment)
            if os.path.isdir(os.path.join(*stack)):
                continue

            print(f'Create {os.path.join(*stack)}')
            os.mkdir(os.path.join(*stack))
            sleep(.1)

        endpoint_mod_path = '.'.join([package, *target.split('/')[1:], *path.split('/')[1:]])
        try:
            endpoint_mod = importlib.import_module(endpoint_mod_path)
            if not hasattr(endpoint_mod, str(elt.method)):
                if endpoint_mod.__path__[0] not in missing_methods:
                    missing_methods[endpoint_mod.__path__[0]] = []

                missing_methods[endpoint_mod.__path__[0]].append(str(elt.method))

        except Exception as exc:
            print(f'Could not import {endpoint_mod_path}, may be a bug')
            print(exc)
            endpoint_mod_path = endpoint_mod_path.replace('.', '/')
            if endpoint_mod_path not in missing_methods:
                missing_methods[endpoint_mod_path] = []

            missing_methods[endpoint_mod_path].append(str(elt.method))

            pass


    for path, methods in missing_methods.items():
        with open(os.path.join(path, '__init__.py'), 'a+') as f:
            for method in methods:
                f.write('\n'.join((
                    f'def {method}():', 
                    '    raise NotImplementedError\n')))
