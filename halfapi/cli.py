#!/usr/bin/env python3
# builtins
import click
import uvicorn
import os
import sys
import re
import importlib
from pprint import pprint

CONTEXT_SETTINGS={
    'default_map':{'run': {}} 
}

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
    from halfapi.conf import (PROJECT_NAME, HOST, PORT,
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


@click.option('--domain', default=None)
@click.option('--update', default=False, is_flag=True)
@cli.command()
def routes(domain, update):
    domains = DOMAINS if domain is None else [domain]
    if update:
        if not domain:
            click.echo('No domain name given, will update all active domains')
        for domain in domains:
            update_db(domain)
    else:
        list_routes(domains)


def list_routes(domains):
    for domain in domains:
        print(f'\nDomain {domain}')
        routes = Acl(domain=domain)
        for route in routes.select():
            print('-', route)

def update_db(domain=None):
    from halfapi.db import (
        Domain,
        APIRouter,
        APIRoute,
        AclFunction,
        Acl)

    global Domain, APIRouter, APIRoute, AclFunction, Acl

    if domain is None:
        from halfapi.conf import DOMAINS

        click.echo('No domain name given, will update all active domains')
        for domain in DOMAINS:
            dbupdate_fct(domain)
        sys.exit(0)

    return dbupdate_fct(domain)


def dbupdate_fct(domain=None):
    if domain is None:
        click.echo('Missing domain', err=True)
        sys.exit(1)
    else:
        click.echo(f'Will update routes for {domain}')

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

        elts = path[1:].split('/')

        fct_name = [http_verb.lower()]
        for elt in elts:
            if elt and elt[0] == '{':
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
    except ImportError:
        click.echo(f"Can't import *{domain}*", err=True)
        return False

    try:
        add_domain()

        # add sub routers
        try:
            ROUTERS = dom_mod.ROUTERS
        except AttributeError:
            click.echo(f'The domain {domain} has no *ROUTERS* variable', err=True)

        for router_name in dom_mod.ROUTERS:
            try:
                router_mod = importlib.import_module(f'.routers.{router_name}', domain)

            except ImportError:
                click.echo(f'The domain {domain} has no *{router_name}* router', err=True)
            add_router(router_name)

            pprint(router_mod.ROUTES)
            for route_path, route_params  in router_mod.ROUTES.items():
                for http_verb, acls in route_params.items():
                    add_route(http_verb, route_path, router_name, acls)


    except Exception as e:
        click.echo(e, err=True)

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

    if repo is not None:
        click.echo(f'Clone URL {repo} in directory {project}')
        pygit2.clone_repository(
            url=repo,
            path=project
        )

    else:
        click.echo(f'Initialize project repository in directory {project}')
        pygit2.init_repository(project)



if __name__ == '__main__':
    cli()
