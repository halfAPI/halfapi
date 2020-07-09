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

@click.option('--envfile', default=None)
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
def run(envfile, host, port, debug, dev, dbname, dbhost, dbport, dbuser, dbpassword):
    if envfile:
        try:
            with open(envfile) as f:
                print('Will use the following env parameters')
                print(f.readlines())
                pass
        except FileNotFoundError:
            print(f'No file named {envfile}')
            envfile = None

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
    db_params['dbname'] = db_params.get('dbname', dbname)
    db_params['host'] = db_params.get('host', dbhost)
    db_params['port'] = db_params.get('port', dbport)
    db_params['user'] = db_params.get('user', dbuser)
    db_params['password'] = db_params.get('password', dbpassword)

    os.environ['HALFORM_DSN'] = dicttodsn(db_params)

    check_conf()

    sys.path.insert(0, os.getcwd())
    click.echo(sys.path)
    uvicorn.run('halfapi.app:app',
        env_file=envfile,
        host=host,
        port=int(port),
        log_level=log_level,
        reload=reload)

@click.option('--dbname', default='api')
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=5432)
@click.option('--user', default='api')
@click.option('--password', default='')
@click.option('--domain', default='organigramme')
@click.option('--drop', is_flag=True, default=False)
@cli.command()
def dbupdate(dbname, host, port, user, password, domain, drop):

    def dropdb():
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

    def delete_domain():
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

    def add_acl_fct(fct):
        acl = AclFunction()
        acl.version = version
        acl.domain = domain
        acl.name = fct.__name__
        if len(acl) == 0:
            acl.insert()

    def add_acl(name, **kwargs):
        acl = Acl()
        acl.version = version
        acl.domain = domain
        acl.name = name
        acl.path = kwargs['path']
        acl.http_verb = kwargs['verb']
        for fct in kwargs['acl']:
            acl.function = fct.__name__

            if len(acl) == 0:
                if fct is not None:
                    add_acl_fct(fct)

                acl.insert()

            elif fct is None:
                acl.delete()


    def add_route(name, **kwargs):
        print(f'Adding route {version}/{domain}/{name}')
        route = Route()
        route.version = version
        route.domain = domain
        route.path = kwargs['path']
        if len(route) == 0:
            route.insert()

    def add_routes_and_acl(routes):
        for name, route_params in routes.items():
            add_route(name, **route_params)
            add_acl(name, **route_params)


    def add_domain():
        new_domain = Domain(name=domain)
        new_domain.version = version
        if len(new_domain) == 0:
            print(f'New domain {domain}')
            new_domain.insert()


    if drop:
        dropdb()

    delete_domain()

    acl_set = set()

    try:

        # module retrieval
        dom_mod = importlib.import_module(domain)

        version = dom_mod.API_VERSION
        add_domain()

        # add main routes
        ROUTES = dom_mod.ROUTES
        add_routes_and_acl(dom_mod.ROUTES)

        # add sub routers
        ROUTERS = dom_mod.ROUTERS

        for router_name in dom_mod.ROUTERS:
            router_mod = importlib.import_module(f'.routers.{router_name}', domain)
            add_routes_and_acl(router_mod.ROUTES)

    except ImportError:
        click.echo(f'The domain {domain} has no *ROUTES* variable', err=True)
    except Exception as e:
        click.echo(e, err=True)





if __name__ == '__main__':
    cli()

