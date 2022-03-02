#!/usr/bin/env python3
"""
Routes module

Fonctions :
    - gen_domain_routes
    - gen_starlette_routes
    - api_routes
    - api_acls

Exception :
    - DomainNotFoundError

"""
import inspect

from typing import Coroutine, Dict, Generator, Tuple, Any
from types import ModuleType, FunctionType

import yaml

# from .domain import gen_router_routes, domain_acls, route_decorator, domain_schema
from .responses import ORJSONResponse
from .acl import args_check
from ..half_route import HalfRoute
from . import acl

from ..logging import logger

class DomainNotFoundError(Exception):
    """ Exception when a domain is not importable
    """

def JSONRoute(data: Any) -> Coroutine:
    """
    Returns a route function that returns the data as JSON

    Parameters:
        data (Any):
            The data to return

    Returns:
        async function
    """
    async def wrapped(request, *args, **kwargs):
        return ORJSONResponse(data)

    return wrapped


def gen_domain_routes(m_domain: ModuleType):
    """
    Yields the Route objects for a domain

    Parameters:
        m_domains: ModuleType

    Returns:
        Generator(HalfRoute)
    """
    yield HalfRoute('/',
        JSONRoute(domain_schema(m_domain)),
        [{'acl': acl.public}],
        'GET'
    )

    for path, method, m_router, fct, params in gen_router_routes(m_domain, []):
        yield HalfRoute(f'/{path}', fct, params, method)


def gen_schema_routes(schema: Dict):
    """
    Yields the Route objects according to a given schema
    """
    for path, methods in schema.items():
        for verb, definition in methods.items():
            fct = definition.pop('fct')
            acls = definition.pop('acls')
            # TODO: Check what to do with gen_routes, it is almost the same function
            if not inspect.iscoroutinefunction(fct):
                yield HalfRoute(path, route_decorator(fct), acls, verb)
            else:
                yield HalfRoute(path, args_check(fct), acls, verb)


def gen_starlette_routes(d_domains: Dict[str, ModuleType]) -> Generator:
    """
    Yields the Route objects for HalfAPI app

    Parameters:
        d_domains (dict[str, ModuleType])

    Returns:
        Generator(Route)
    """
    for domain_name, m_domain in d_domains.items():
        yield from gen_domain_routes(m_domain)


def api_routes(m_dom: ModuleType) -> Tuple[Dict, Dict]:
    """
    Yields the description objects for HalfAPI app routes

    Parameters:
        m_dom (ModuleType): the halfapi module

    Returns:
        (Dict, Dict)
    """

    d_acls = {}

    def str_acl(params):
        l_params = []

        for param in params:

            if 'acl' not in param.keys() or not param['acl']:
                continue

            l_params.append(param.copy())
            l_params[-1]['acl'] = param['acl'].__name__

            if param['acl'] not in d_acls.keys():
                d_acls[param['acl'].__name__] = param['acl']

        return l_params

    d_res = {}
    for path, verb, m_router, fct, params in gen_router_routes(m_dom, []):
        try:
            if path not in d_res:
                d_res[path] = {}

            d_res[path][verb] = {
                'docs': yaml.load(fct.__doc__, Loader=yaml.FullLoader),
                'acls': str_acl(params)
            }
        except Exception as exc:
            logger.error("""Error in route generation
                path:%s
                verb:%s
                router:%s
                fct:%s
                params:%s """, path, verb, m_router, fct, params)
            raise exc

    return d_res, d_acls


def api_acls(request):
    """ Returns the list of possible ACLs

    # TODO: Rewrite
    """
    res = {}
    domains = {}
    doc = 'doc' in request.query_params
    for domain, m_domain in domains.items():
        res[domain] = {}
        for acl_name, fct in domain_acls(m_domain, [domain]):
            if not isinstance(fct, FunctionType):
                continue

            fct_result = fct.__doc__.strip() if doc and fct.__doc__ else fct(request)
            if acl_name in res[domain]:
                continue

            if isinstance(fct_result, FunctionType):
                fct_result = fct()(request)
            res[domain][acl_name] = fct_result

    return res
