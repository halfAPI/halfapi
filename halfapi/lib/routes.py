#!/usr/bin/env python3
from functools import wraps
import importlib
import sys
from typing import Callable, List, Tuple, Dict

from halfapi.conf import (PROJECT_NAME, DB_NAME, HOST, PORT,
    PRODUCTION, DOMAINS)

from halfapi.db import (
    Domain,
    APIRouter,
    APIRoute,
    AclFunction,
    Acl)
from halfapi.lib.responses import *
from halfapi.lib.domain import domain_scanner
from starlette.exceptions import HTTPException
from starlette.routing import Mount, Route
from starlette.requests import Request

class DomainNotFoundError(Exception):
    pass

def route_decorator(fct: Callable, acls_mod, params: List[Dict]):
    @wraps(fct)
    async def caller(req: Request, *args, **kwargs):
        for param in params:
            acl_fct = getattr(acls_mod, param['acl'])
            if acl_fct(req, *args, **kwargs):
                """
                    We the 'acl' and 'keys' kwargs values to let the
                    decorated function know which ACL function answered
                    True, and which keys the request will return
                """
                return await fct(
                    req, *args,
                    **{
                        **kwargs,
                        **params
                    })

        raise HTTPException(401)

    return caller

def gen_starlette_routes():
    for domain in DOMAINS:
        domain_acl_mod = importlib.import_module(
            f'{domain}.acl')

        ( Route(route['path'],
            route_decorator(
                route['fct'],
                domain_acl_mod,
                route['params'],
            ), methods=[route['verb']])
            for route in domain_scanner(domain)
        )

        for route in gen_routes(domain):

            yield (
                Route(route['path'],
                route_decorator(
                    route['fct'],
                    domain_acl_mod,
                    route['params'],
                ), methods=[route['verb']])
            )
