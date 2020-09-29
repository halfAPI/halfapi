#!/usr/bin/env python3
from functools import wraps
import importlib
import sys
from typing import Callable, List, Tuple, Dict

from halfapi.conf import (PROJECT_NAME, DB_NAME, HOST, PORT,
    PRODUCTION, DOMAINS)

# from halfapi.db import (
#     Domain,
#     APIRouter,
#     APIRoute,
#     AclFunction,
#     Acl)
from halfapi.lib.responses import *
from halfapi.lib.domain import gen_domain_routes
from starlette.exceptions import HTTPException
from starlette.routing import Mount, Route
from starlette.requests import Request

class DomainNotFoundError(Exception):
    pass

def route_acl_decorator(fct: Callable, acls_mod, params: List[Dict]):
    """
    Decorator for async functions that calls pre-conditions functions
    and appends kwargs to the target function


    Parameters:
        fct (Callable):
            The function to decorate
        acls_mod (Module):
            The module that contains the pre-condition functions (acls)

        params List[Dict]:
            A list of dicts that have an "acl" key that points to a function

    Returns:
        async function
    """

    @wraps(fct)
    async def caller(req: Request, *args, **kwargs):
        for param in params:
            if param.get('acl') and param['acl'](req, *args, **kwargs):
                """
                We merge the 'acl' and 'keys' kwargs values to let the
                decorated function know which ACL function answered
                True, and other parameters that you'd need
                """
                return await fct(
                    req, *args,
                    **{
                        **kwargs,
                        **param
                    })

        raise HTTPException(401)

    return caller

###
# testing purpose only
def acl_mock(fct):
    return lambda r, *a, **kw: True
#
##

def gen_starlette_routes(m_dom):
    """
    Yields the Route objects for HalfAPI app

    Parameters:
        m_dom (module): the halfapi module

    Returns:
        Generator[Route]
    """

    m_dom_acl = importlib.import_module('.acl', m_dom.__name__)

    for route in gen_domain_routes(m_dom.__name__):
        yield (
            Route(route['path'],
                route_acl_decorator(
                    route['fct'],
                    m_dom_acl,
                    route['params'],
                ),
                methods=[route['verb']])
        )


def api_routes(m_dom):
    """
    Yields the description objects for HalfAPI app routes

    Parameters:
        m_dom (module): the halfapi module

    Returns:
        Generator[Dict]
    """

    m_dom_acl = importlib.import_module('.acl', m_dom.__name__)

    def pop_acl(r):
        if 'acl' in r.keys():
            r.pop('acl')
        print(r)
        return r

    return {
        route['path']: {
            'params': list(map(pop_acl, route['params'])),
            'verb': route['verb'],
            'fqtn': route['fqtn']
        }
        for route in gen_domain_routes(m_dom.__name__)
    }
    