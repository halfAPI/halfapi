#!/usr/bin/env python3

# builtins
import click
import uvicorn
import os
import sys
import importlib

# database
import psycopg2

# hop-generated classes
from .models.api.version import Version
from .models.api.domain import Domain
from .models.api.route import Route
from .models.api.acl_function import AclFunction
from .models.api.acl import Acl

# module libraries
from .app import check_conf

HALFORM_DSN=''
HALFORM_SECRET=''
CONTEXT_SETTINGS={
    'default_map':{'run': {'port': 8000}} 
}

@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None: 
        return run()

@click.option('--host', default='127.0.0.1')
@click.option('--port', default='8000')
@click.option('--debug', default=False)
@click.option('--dev', default=True)
@click.option('--dbname', default='api')
@click.option('--dbhost', default='127.0.0.1')
@click.option('--dbport', default=5432)
@click.option('--dbuser', default='api')
@click.option('--dbpassword', default='')
@cli.command()
def run(host, port, debug, dev, dbname, dbhost, dbport, dbuser, dbpassword):
    if dev:
        debug = True
        reload = True
        log_level = 'debug'
    else:
        reload = False
        log_level = 'info'

    # Helper function to convert the string-based dsn to a dict
    dsntodict = lambda dsn: dict(
        map(lambda x:
            map(lambda y: y.strip("'\""),
            x.split('=')
            ),
        dsn.split()))

    dicttodsn = lambda dsn_d: (' '.join(
        [ '{key}={val}'.format(key=key, val=dsn_d[key])
          for key in dsn_d.keys()
        ]
    ))

    click.echo('Launching application with default parameters')
    click.echo(f'''Parameters : \n
    Host : {host}
    Port : {port}
    Debug : {debug}
    Dev : {dev}''')

    HALFORM_DSN=os.environ.get('HALFORM_DSN', '')
    db_params = dsntodict(HALFORM_DSN)
    if not hasattr(db_params, 'dbname'):
        db_params['dbname'] = dbname
    if not hasattr(db_params, 'host'):
        db_params['host'] = dbhost
    if not hasattr(db_params, 'port'):
        db_params['port'] = dbport
    if not hasattr(db_params, 'user'):
        db_params['user'] = dbuser
    if not hasattr(db_params, 'password'):
        db_params['password'] = dbpassword

    os.environ['HALFORM_DSN'] = dicttodsn(db_params)

    check_conf()

    sys.path.insert(0, os.getcwd())
    click.echo(sys.path)
    uvicorn.run('halfapi.app:app',
        host=host,
        port=int(port),
        log_level=log_level,
        reload=reload)

def dropdb(dbname, host, port, user, password):
    if not click.confirm(f'Will now drop database {dbname}', default=True):
        return False

    conn = psycopg2.connect({
        'dbname': dbname,
        'host': host,
        'port': port,
        'user': user,
        'password': password
    })

    cur = conn.cursor()

    cur.execute(f'DROP DATABASE {dbname};')
    conn.commit()
    cur.close()
    conn.close()

    return True

def delete_domain(domain):
    d = Domain(name=domain)
    if len(d) < 1:
        return False

    acl = Acl(domain=domain)
    acl.delete()

    fct = AclFunction(domain=domain)
    fct.delete()

    route = Route(domain=domain)
    route.delete()

    d.delete()

    return True

def add_acl_fct(version, domain_name, fct):
    acl = Acl()
    acl.version = version
    acl.domain = domain_name
    acl.name = fct.__name__
    acl.insert()

def add_route(version, domain_name, name, **kwargs):
    route = Route()
    route.version = version
    route.domain = domain_name
    route.path = kwargs['path']
    route.insert()


def add_routes(version, domain_name, routes):
    for name, route_params in routes.items():
        print(f'Adding route {version}/{domain_name}/{function_name}')
        add_route(version, domain_name, name, **route_params)


def add_domain(version, domain_name):
    domain = Domain(name=domain_name)
    domain.version = version
    if len(domain) == 0:
        print(f'New domain {domain_name}')
        domain.insert()

@click.option('--dbname', default='api')
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=5432)
@click.option('--user', default='api')
@click.option('--password', default='')
@click.option('--domain', default='organigramme')
@click.option('--drop', is_flag=True, default=False)
@cli.command()
def dbupdate(dbname, host, port, user, password, domain, drop):
    if drop:
        dropdb(dbname, host, port, user, password)

    delete_domain(domain)

    acl_set = set()
    add_route_acl = lambda routes: [
        [ acl_set.add(acl) for acl in route['acl'] ]
        for route in routes.keys() ]

    try:
        dom_mod = importlib.import_module(domain)

        API_VERSION = dom_mod.API_VERSION
        add_domain(API_VERSION, domain)

        ROUTES = dom_mod.ROUTES
        add_route_acl(ROUTES)
        add_routes(API_VERSION, domain, dom_mod.ROUTES)

        ROUTERS = dom_mod.ROUTERS

        for router_name in dom_mod.ROUTERS:
            router_mod = importlib.import_module(f'.routers.{router_name}', domain)
            add_route_acl(router_mod.ROUTES)
            add_routes(API_VERSION, domain, router_mod.ROUTES)

        for acl in acl_set:
            add_acl_fct(API_VERSION, domain, acl)

    except ImportError:
        click.echo(f'The domain {domain} has no *ROUTES* variable', err=True)
    except Exception as e:
        click.echo(e, err=True)





if __name__ == '__main__':
    cli()

