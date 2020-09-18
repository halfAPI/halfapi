#!/usr/bin/env python3
from functools import wraps
import importlib
import sys
from typing import Callable, List, Tuple

from halfapi.conf import (PROJECT_NAME, DB_NAME, HOST, PORT,
    PRODUCTION, DOMAINS)

from halfapi.db import (
    Domain,
    APIRouter,
    APIRoute,
    AclFunction,
    Acl)
from halfapi.lib.responses import *
from starlette.exceptions import HTTPException
from starlette.routing import Mount, Route
from starlette.requests import Request

class DomainNotFoundError(Exception):
    pass

def get_routes(domains=None):
    """ Procedure to mount the registered domains on their prefixes

        Parameters:

            - app (ASGIApp): The Starlette instance
            - domains (list): The domains to mount, retrieved from the database
              with their attributes "name"

        Returns: Nothing
    """


    def route_decorator(fct: Callable, acls_mod, acls: List[Tuple]):
        @wraps(fct)
        async def caller(req: Request, *args, **kwargs):
            for acl_fct_name, keys in acls:
                acl_fct = getattr(acls_mod, acl_fct_name)
                if acl_fct(req, *args, **kwargs):
                    return await fct(req, *args, **{ **kwargs, **{'keys': keys} })

            raise HTTPException(401)

        return caller

    app_routes = []
    for domain_name in DOMAINS:
        try:
            domain = next(Domain(name=domain_name).select())
        except StopIteration:
            raise DomainNotFoundError(
                f"Domain '{domain_name}' not found in '{DB_NAME}' database!")
        domain_acl_mod = importlib.import_module(f'{domain["name"]}.acl')
        domain_routes = []
        for router in APIRouter(domain=domain['name']).select():
            router_routes = []

            router_mod = importlib.import_module(
                '{domain}.routers.{name}'.format(**router))

            with APIRoute(domain=domain['name'],
                router=router['name']) as routes:
                for route in routes.select():
                    fct_name = route.pop('fct_name')
                    acls = [ (elt['acl_fct_name'], elt['keys']) 
                        for elt in Acl(**route).select('acl_fct_name', 'keys') ]

                    router_routes.append(
                        Route(route['path'], 
                        route_decorator(
                            getattr(router_mod, fct_name),
                            domain_acl_mod,
                            acls
                        ), methods=[route['http_verb']])
                    )

            domain_routes.append(
                Mount('/{name}'.format(**router), routes=router_routes))

        app_routes.append(Mount('/{name}'.format(**domain),
            routes=domain_routes))
    return app_routes 
