#!/usr/bin/env python3
from halfapi.conf import (PROJECT_NAME, HOST, PORT,
    PRODUCTION,
    BASE_DIR)

from halfapi.db import (
    Domain,
    APIRouter,
    APIRoute,
    AclFunction,
    Acl)

# builtins
import click
import uvicorn
import os
import sys
import importlib
from pprint import pprint

CONTEXT_SETTINGS={
    'default_map':{'run': {}} 
}

@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None: 
        return run()


@click.option('--host', default=HOST)
@click.option('--port', default=PORT)
@cli.command()
def run(host, port):
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


@click.option('--domain', default=None)
@cli.command()
def dbupdate(domain):

    def add_acl_fct(fct):
        acl = AclFunction()
        acl.domain = domain
        acl.name = fct.__name__
        if len(acl) == 0:
            acl.insert()


    def add_acls(acls, **route):
        route.pop('fct_name')
        acl = Acl(**route)

        for fct in acls:
            acl.acl_fct_name = fct.__name__

            if len(acl) == 0:
                if fct is not None:
                    add_acl_fct(fct)

                acl.insert()

            elif fct is None:
                acl.delete()


    def get_fct_name(http_verb, path):
        if path[0] != '/':
            raise Exception('Malformed path')

        elts = [] if len(path) == 1 else path[1:].split('/')

        fct_name = [http_verb.lower()]
        for elt in elts:
            if elt[0] == '{':
                fct_name.append(elt[1:-1].split(':')[0].upper())
            else:
                fct_name.append(elt)

        return '_'.join(fct_name)


    def add_router(name):
        router = APIRouter()
        router.name = name
        router.domain = domain

        if len(router) == 0:
            router.insert()


    def add_route(http_verb, path, router, acls):
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


    def add_domain():
        new_domain = Domain(name=domain)
        if len(new_domain) == 0:
            click.echo(f'New domain {domain}')
            new_domain.insert()

    sys.path.insert(0, BASE_DIR)

    delete_domain(domain)

    acl_set = set()

    try:

        # module retrieval
        dom_mod = importlib.import_module(domain)

        add_domain()

        # add sub routers
        ROUTERS = dom_mod.ROUTERS

        for router_name in dom_mod.ROUTERS:
            router_mod = importlib.import_module(f'.routers.{router_name}', domain)
            add_router(router_name)

            pprint(router_mod.ROUTES)
            for route_path, route_params  in router_mod.ROUTES.items():
                for http_verb, acls in route_params.items():
                    add_route(http_verb, route_path, router_name, acls)


    except ImportError:
        click.echo(f'The domain {domain} has no *ROUTES* variable', err=True)
    except Exception as e:
        click.echo(e, err=True)


if __name__ == '__main__':
    cli()
