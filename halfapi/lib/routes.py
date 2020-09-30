#!/usr/bin/env python3
from functools import wraps
import importlib
import sys
from typing import Callable, List, Tuple, Dict, Generator
from types import ModuleType

from halfapi.conf import (PROJECT_NAME, DB_NAME, HOST, PORT,
    PRODUCTION, DOMAINS)

from halfapi.lib.responses import *
from halfapi.lib.domain import gen_domain_routes, VERBS
from starlette.exceptions import HTTPException
from starlette.routing import Mount, Route
from starlette.requests import Request

class DomainNotFoundError(Exception):
    pass

def route_acl_decorator(fct: Callable, params: List[Dict]):
    """
    Decorator for async functions that calls pre-conditions functions
    and appends kwargs to the target function


    Parameters:
        fct (Callable):
            The function to decorate

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

def gen_starlette_routes(m_dom: ModuleType) -> Generator:
    """
    Yields the Route objects for HalfAPI app

    Parameters:
        m_dom (ModuleType): the halfapi module

    Returns:
        Generator(Route)
    """

    m_dom_acl = importlib.import_module('.acl', m_dom.__name__)

    for path, d_route in gen_domain_routes(m_dom.__name__):
        for verb in VERBS:
            if verb not in d_route.keys():
                continue

            yield (
                Route(path,
                    route_acl_decorator(
                        d_route[verb]['fct'],
                        d_route[verb]['params']
                    ),
                    methods=[verb])
            )


def api_routes(m_dom: ModuleType) -> Generator:
    """
    Yields the description objects for HalfAPI app routes

    Parameters:
        m_dom (ModuleType): the halfapi module

    Returns:
        Generator(Dict)
    """

    m_dom_acl = importlib.import_module('.acl', m_dom.__name__)
    d_acls = {}

    def str_acl(params):
        l_params = []
        access = None

        for param in params:
            if 'acl' not in param.keys():
                continue

            l_params.append(param.copy())
            l_params[-1]['acl'] = param['acl'].__name__

            if param['acl'] not in d_acls.keys():
                d_acls[param['acl'].__name__] = param['acl']

        return l_params

    d_res = {}
    for path, d_route in gen_domain_routes(m_dom.__name__):
        d_res[path] = {'fqtn': d_route['fqtn'] }

        for verb in VERBS:
            if verb not in d_route.keys():
                continue
            d_res[path][verb] = str_acl(d_route[verb]['params'])

    return d_res, d_acls


def api_acls(request):
    from .. import app
    res = {}
    for domain in app.d_acl.keys():
        res[domain] = {}
        for acl_name, fct in app.d_acl[domain].items():
            print( fct(request) )
            res[domain][acl_name] = fct(request)

    return res
