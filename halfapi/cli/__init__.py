#!/usr/bin/env python3
# builtins
import click
import uvicorn
import os
import sys
import re
import importlib
import logging
from pprint import pprint
from configparser import ConfigParser

from halfapi import __version__
from halfapi.cli.lib.db import ProjectDB

CONTEXT_SETTINGS = {
    'default_map':{'run': {}} 
}

TMPL_HALFAPI_ETC = """Insert this into the HALFAPI_CONF_DIR/{project} file

[project]
host = 127.0.0.1 
port = 8000
secret = /path/to/secret_file
production = False
base_dir = {base_dir}
"""

TMPL_HALFAPI_CONFIG = """[project]
name = {name}
halfapi_version = {halfapi_version}
"""

logger = logging.getLogger('halfapi')

@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.option('--version', is_flag=True)
@click.pass_context
def cli(ctx, version):
    if version:
        import halfapi
        return click.echo(halfapi.version())

    if ctx.invoked_subcommand is None: 
        return run()

@click.option('--host', default=None)
@click.option('--port', default=None)
@cli.command()
def run(host, port):
    from halfapi.conf import (HOST, PORT,
        PRODUCTION, BASE_DIR)

    if not host:
        host = HOST

    if not port:
        port = PORT

    port = int(port)

    debug = reload = not PRODUCTION
    log_level = 'info' if PRODUCTION else 'debug'

    click.echo('Launching application')

    sys.path.insert(0, BASE_DIR)
    click.echo(f'current python_path : {sys.path}')

    uvicorn.run('halfapi.app:application',
        host=host,
        port=int(port),
        log_level=log_level,
        reload=reload)


def delete_domain(domain):
    d = Domain(name=domain)
    if len(d) != 1:
        return False

    d.delete(delete_all=True)
    return True


@click.option('--domain', '-d', default=None, multiple=True)
@click.option('--update', default=False, is_flag=True)
@cli.command()
def routes(domain, update):
    """
    Lists routes for the specified domains, or update them in the database

    Parameters:
        domain (List[str]|None): The list of the domains to list/update

        The parameter has a misleading name as it is a multiple option
        but this would be strange to use it several times named as "domains"

        update (boolean): If set, update the database for the selected domains
    """
    from halfapi.db import (
        Domain,
        APIRouter,
        APIRoute,
        AclFunction,
        Acl)

    global Domain, APIRouter, APIRoute, AclFunction, Acl

    from halfapi.conf import DOMAINS
    if not domain:
        domain = DOMAINS
    else:
        for domain_name in domain:
            if domain_name in DOMAINS:
                continue
            click.echo(
                f'Domain {domain}s is not activated in the configuration')

    if update:
        update_db(domain)
    else:
        list_routes(domain)


def list_routes(domains):
    for domain in domains:
        print(f'\nDomain {domain}')
        routes = Acl(domain=domain)
        for route in routes.select():
            print('-', route)


def update_db(domains):
    from halfapi.conf import BASE_DIR

    def add_domain(domain):
        """
        Inserts Domain into database

        Parameters:
            - domain (str): The domain's name
        """
        new_domain = Domain(name=domain)
        if len(new_domain) == 0:
            click.echo(f'New domain {domain}')
            new_domain.insert()


    def add_router(name, domain):
        """
        Inserts Router into database

        Parameters:
            - name (str): The Router's name
        """
        router = APIRouter()
        router.name = name
        router.domain = domain

        if len(router) == 0:
            router.insert()


    def add_acl_fct(fct, domain):
        """
        Inserts ACL function into database

        Parameters:
            - fct (Callable): The ACL function reference
            - domain (str): The Domain's name
        """
        acl = AclFunction()
        acl.domain = domain
        acl.name = fct.__name__
        if len(acl) == 0:
            acl.insert()


    def add_acls(acls, **route):
        """
        Inserts ACL into database

        Parameters:
            - acls (List[Callable]): List of the Route's ACL's
            - route (dict): The Route
        """
        route.pop('fct_name')
        acl = Acl(**route)

        for fct in acls:
            acl.acl_fct_name = fct.__name__

            if len(acl) == 0:
                if fct is not None:
                    add_acl_fct(fct, route['domain'])

                acl.insert()

            elif fct is None:
                acl.delete()


    def get_fct_name(http_verb, path):
        """
        Returns the predictable name of the function for a route

        Parameters:
            - http_verb (str): The Route's HTTP method (GET, POST, ...)
            - path (str): A path beginning by '/' for the route

        Returns:
            str: The *unique* function name for a route and it's verb


        Examples:

            >>> get_fct_name('foo', 'bar')
            Traceback (most recent call last):
                ...
            Exception: Malformed path

            >>> get_fct_name('get', '/')
            'get_'

            >>> get_fct_name('GET', '/')
            'get_'

            >>> get_fct_name('POST', '/foo')
            'post_foo'

            >>> get_fct_name('POST', '/foo/bar')
            'post_foo_bar'

            >>> get_fct_name('DEL', '/foo/{boo}/{far}/bar')
            'del_foo_BOO_FAR_bar'

            >>> get_fct_name('DEL', '/foo/{boo:zoo}')
            'del_foo_BOO'
        """

        if path[0] != '/':
            raise Exception('Malformed path')

        elts = path[1:].split('/')

        fct_name = [http_verb.lower()]
        for elt in elts:
            if elt and elt[0] == '{':
                fct_name.append(elt[1:-1].split(':')[0].upper())
            else:
                fct_name.append(elt)

        return '_'.join(fct_name)


    def add_route(http_verb, path, router, domain, acls):
        """
        Inserts Route into database

        Parameters:
            - http_verb (str): The Route's HTTP method (GET, POST, ...)
            - path (str): A path beginning by '/' for the route
            - router (str): The Route's Router name
            - domain (str): The Domain's name
            - acls (List[Callable]): The list of ACL functions for this Route
        """

        click.echo(f'Adding route /{domain}/{router}{path}')
        route = APIRoute()
        route.http_verb = http_verb
        route.path = path
        route.fct_name = get_fct_name(http_verb, path)
        route.router = router
        route.domain = domain

        if len(route) == 0:
            route.insert()

        add_acls(acls, **route.to_dict())


    sys.path.insert(0, BASE_DIR)

    for domain in domains:
        # Reset Domain relations
        delete_domain(domain)

        acl_set = set()

        try:
            # Module retrieval
            dom_mod = importlib.import_module(domain)
        except ImportError:
            # Domain is not available in current PYTHONPATH
            click.echo(f"Can't import *{domain}*", err=True)
            continue

        try:
            add_domain(domain)
        except Exception as e:
            # Could not insert Domain
            # @TODO : Insertion exception handling
            print(e)
            click.echo(f"Could not insert *{domain}*", err=True)
            continue

        # add sub routers
        try:
            ROUTERS = dom_mod.ROUTERS
        except AttributeError:
            # No ROUTERS variable in current domain, check domain/__init__.py
            click.echo(f'The domain {domain} has no *ROUTERS* variable', err=True)

        for router_name in dom_mod.ROUTERS:
            try:
                router_mod = getattr(dom_mod.routers, router_name)
            except AttributError:
                # Missing router, continue 
                click.echo(f'The domain {domain} has no *{router_name}* router', err=True)
                continue

            try:
                add_router(router_name, domain)
            except Exception as e:
                # Could not insert Router
                # @TODO : Insertion exception handling
                print(e)
                continue


            for route_path, route_params  in router_mod.ROUTES.items():
                for http_verb, acls in route_params.items():
                    try:
                        # Insert a route and it's ACLS
                        add_route(http_verb, route_path, router_name, domain, acls)
                    except Exception as e:
                        # Could not insert route
                        # @TODO : Insertion exception handling
                        print(e)
                        continue


@click.argument('project')
@click.option('--repo', default=None)
@cli.command()
def init_project(project, repo):
    import pygit2

    if not re.match('^[a-z0-9_]+$', project, re.I):
        click.echo('Project name must match "^[a-z0-9_]+$", retry.', err=True)
        sys.exit(1)

    if os.path.exists(project):
        click.echo(f'A file named {project} already exists, abort.', err=True)
        sys.exit(1)


    click.echo(f'Initialize project repository in directory {project}')
    pygit2.init_repository(project)

    try:
        pdb = ProjectDB(project)
        pdb.init()
    except Exception as e:
        logger.warning(e)
        logger.debug(os.environ.get('HALFORM_CONF_DIR'))
        raise e

    os.mkdir(os.path.join(project, '.halfapi'))
    open(os.path.join(project, '.halfapi', 'domains'), 'w').write('')
    config_file = os.path.join(project, '.halfapi', 'config')
    with open(config_file, 'w') as f:
        f.write(TMPL_HALFAPI_CONFIG.format(
            name=project,
            halfapi_version=__version__
        ))

    print(TMPL_HALFAPI_ETC.format(
        project=project,
        base_dir=os.path.abspath(project)
    ))

if __name__ == '__main__':
    cli()