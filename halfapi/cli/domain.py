#!/usr/bin/env python3
# builtins
import sys
import logging
import click
import importlib


from .cli import cli
from halfapi.conf import DOMAINS, DOMAINSDICT, BASE_DIR

from halfapi.lib.schemas import schema_dict_dom
# from halfapi.db import (
#     Domain,
#     APIRouter,
#     APIRoute,
#     AclFunction,
#     Acl)

logger = logging.getLogger('halfapi')

#################
# domain create #
#################
def create_domain():
    sys.exit(0)


###############
# domain read #
###############
def list_routes(domain):
    click.echo(f'\nDomain : {domain}')

    m_dom = DOMAINSDICT[domain]
    for key, item in schema_dict_dom(m_dom).get('paths', {}).items():
        methods = '|'.join(list(item.keys()))
        click.echo(f'{key} : {methods}')


#################
# domain update #
#################
def update_db(domain):

    def add_domain():
        """
        Inserts Domain into database
        """
        new_domain = Domain(name=domain)
        if len(new_domain) == 0:
            click.echo(f'New domain {domain}')
            new_domain.insert()


    def add_router(name):
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


    def add_acl_fct(fct):
        """
        Inserts ACL function into database

        Parameters:
            - fct (Callable): The ACL function reference
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
            - acls [(Callable, [str])]: List of the Route's ACL's
            - route (dict): The Route
        """
        route.pop('fct_name')
        acl = Acl(**route)

        for fct, keys in acls:
            acl.acl_fct_name = fct.__name__

            if len(acl) != 0:
                raise Exception(
                    'An ACL row for this route with this function already exists. Check your routers')
            else:
                acl.keys = keys
                add_acl_fct(fct)
                acl.insert()




    def add_route(http_verb, path, router, acls):
        """
        Inserts Route into database

        Parameters:
            - http_verb (str): The Route's HTTP method (GET, POST, ...)
            - path (str): A path beginning by '/' for the route
            - router (str): The Route's Router name
            - acls (List[Callable]): The list of ACL functions for this Route
        """

        click.echo(f'Adding route /{domain}/{router}{path}')

        route = APIRoute()
        # Route definition
        route.http_verb = http_verb
        route.path = path
        route.fct_name = get_fct_name(http_verb, path)
        route.router = router
        route.domain = domain

        if len(route) == 0:
            route.insert()

        add_acls(acls, **route.to_dict())


    sys.path.insert(0, BASE_DIR)

    # Reset Domain relations
    delete_domain(domain)

    acl_set = set()

    try:
        # Module retrieval
        dom_mod = importlib.import_module(domain)
    except ImportError:
        # Domain is not available in current PYTHONPATH
        click.echo(f"Can't import *{domain}*", err=True)
        return False

    try:
        add_domain()
    except Exception as e:
        # Could not insert Domain
        # @TODO : Insertion exception handling
        click.echo(e)
        click.echo(f"Could not insert *{domain}*", err=True)
        return False

    # add sub routers
    try:
        ROUTERS = dom_mod.ROUTERS
    except AttributeError:
        # No ROUTERS variable in current domain, check domain/__init__.py
        click.echo(f'The domain {domain} has no *ROUTERS* variable', err=True)

    for router_name in dom_mod.ROUTERS:
        try:
            router_mod = None
            for router_subname in router_name.split('.'):
                router_mod = getattr(router_mod or dom_mod.routers, router_subname)

        except AttributeError:
            # Missing router, continue 
            click.echo(f'The domain {domain} has no *{router_name}* router', err=True)
            continue


        try:
            add_router(router_name)
        except Exception as e:
            # Could not insert Router
            # @TODO : Insertion exception handling
            print(e)
            continue


        d_routes = {}

        if hasattr(router_mod, 'ROUTES'):
            d_routes.update(router_mod.ROUTES)
        else:
            logger.warning(f'{router_name} is missing a ROUTES variable')

        if hasattr(router_mod, 'ROUTERS'):
            for router_router in router_mod.ROUTERS:
                if hasattr(router_router, 'ROUTES'):
                    d_routes.update(router_routes.ROUTES)
                else:
                    logger.warning(f'{router_name}.{router_router.__name__} is missing a ROUTES variable')
        else:
            logger.warning(f'{router_mod} is missing a ROUTERS variable')

        for route_path, route_params  in d_routes.items():
            for http_verb, acls in route_params.items():
                try:
                    # Insert a route and it's ACLS
                    add_route(http_verb, route_path, router_name, acls)
                except Exception as e:
                    # Could not insert route
                    # @TODO : Insertion exception handling
                    print(e)
                    continue


#################
# domain delete #
#################
def delete_domain(domain):
    d = Domain(name=domain)
    if len(d) != 1:
        return False

    d.delete(delete_all=True)
    return True


@click.option('--read',default=False, is_flag=True)
@click.option('--create',default=False, is_flag=True)
@click.option('--update',default=False, is_flag=True)
@click.option('--delete',default=False, is_flag=True)
@click.option('--domains',default=None)
@cli.command()
def domain(domains, delete, update, create, read):  #, domains, read, create, update, delete):
    """
    Lists routes for the specified domains, or update them in the database

    Parameters:
        domain (List[str]|None): The list of the domains to list/update

        The parameter has a misleading name as it is a multiple option
        but this would be strange to use it several times named as "domains"

        update (boolean): If set, update the database for the selected domains
    """

    if not domains:
        if create:
            raise NotImplementedError
            return create_domain()

        domains = DOMAINS
    else:
        domains_ = []
        for domain_name in domains.split(','):
            if domain_name in DOMAINS:
                domains_.append(domain_name)
                continue

            click.echo(
                f'Domain {domain_name}s is not activated in the configuration')

        domains = domains_

    for domain in domains:
        if update:
            raise NotImplementedError
            update_db(domain)
        if delete:
            raise NotImplementedError
            delete_domain(domain)
        else:
            list_routes(domain)


