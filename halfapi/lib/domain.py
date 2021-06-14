#!/usr/bin/env python3
"""
lib/domain.py The domain-scoped utility functions
"""

import os
import sys
import importlib
import logging
from types import ModuleType, FunctionType
from typing import Generator, Dict, List

from halfapi.lib import acl

logger = logging.getLogger("uvicorn.asgi")

VERBS = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')

def get_fct_name(http_verb: str, path: str) -> str:
    """
    Returns the predictable name of the function for a route

    Parameters:
        - http_verb (str): The Route's HTTP method (GET, POST, ...)
        - path (str): The functions path

    Returns:
        str: The *unique* function name for a route and it's verb


    Examples:

        >>> get_fct_name('get', '')
        'get'

        >>> get_fct_name('GET', '')
        'get'

        >>> get_fct_name('POST', 'foo')
        'post_foo'

        >>> get_fct_name('POST', 'bar')
        'post_bar'

        >>> get_fct_name('DEL', 'foo/{boo}')
        'del_foo_BOO'

        >>> get_fct_name('DEL', '{boo:zoo}/far')
        'del_BOO_far'
    """
    if path and path[0] == '/':
        path = path[1:]

    fct_name = [http_verb.lower()]
    for elt in path.split('/'):
        if elt and elt[0] == '{':
            fct_name.append(elt[1:-1].split(':')[0].upper())
        elif elt:
            fct_name.append(elt)

    return '_'.join(fct_name)

def gen_routes(route_params: Dict, path: List, m_router: ModuleType) -> Generator:
    """
    Generates a tuple of the following form for a specific path:

    "/path/to/route", {
        "GET": {
            "fct": endpoint_fct,
            "params": [
                { "acl": acl_fct, [...] }
            ]
        },
        [...]
    }

    Parameters:

        - route_params (Dict): Contains the following keys :
            - one or more HTTP VERB (if none, route is not treated)
            - one or zero FQTN (if none, fqtn is set to None)

        - path (List): The route path, as a list (each item being a level of
            deepness), from the lowest level (domain) to the highest

        - m_router (ModuleType): The parent router module

    Yields:

        (str, Dict): The path routes description

    """
    d_res = {'fqtn': route_params.get('FQTN')}

    for verb in VERBS:
        params = route_params.get(verb)
        if params is None:
            continue
        if len(params) == 0:
            logger.error('No ACL for route [{%s}] %s', verb, "/".join(path))

        try:
            fct_name = get_fct_name(verb, path[-1])
            fct = getattr(m_router, fct_name)
            logger.debug('%s defined in %s', fct.__name__, m_router.__name__)
        except AttributeError as exc:
            logger.error('%s is not defined in %s', fct_name, m_router.__name__)
            continue

        d_res[verb] = {'fct': fct, 'params': params}

    if len(d_res.keys()) > 1:
        yield f"/{'/'.join([ elt for elt in path if elt ])}", d_res


def gen_router_routes(m_router: ModuleType, path: List[str]) -> Generator:
    """
    Recursive generatore that parses a router (or a subrouter)
    and yields from gen_routes

    Parameters:

        - m_router (ModuleType): The currently treated router module
        - path (List[str]): The current path stack

    Yields:

        (str, Dict): The path routes description from **gen_routes**
    """

    if not hasattr(m_router, 'ROUTES'):
        routes = {'':{}}
        for verb in VERBS:
            if hasattr(m_router, verb.lower()):
                routes[''][verb.upper()] = [{
                    'acl': acl.public
                }]
            else:
                print(f'no {verb.lower()} in {m_router}')

        routes['']['SUBROUTES'] = []
        for item in os.listdir(list(m_router.__path__)[0]):
            if os.path.isdir(os.path.join(list(m_router.__path__)[0], item)):
                routes['']['SUBROUTES'].append(item)
    else:
        routes = getattr(m_router, 'ROUTES')

    for subpath, route_params in routes.items():
        path.append(subpath)

        yield from gen_routes(route_params, path, m_router)

        subroutes = route_params.get('SUBROUTES', [])
        for subroute in subroutes:
            logger.debug('Processing subroute **%s** - %s', subroute, m_router.__name__)
            path.append(subroute)
            try:
                submod = importlib.import_module(f'.{subroute}', m_router.__name__)
            except ImportError as exc:
                logger.error('Failed to import subroute **{%s}**', subroute)
                raise exc

            yield from gen_router_routes(submod, path)

            path.pop()

        path.pop()


def d_domains(config) -> Dict[str, ModuleType]:
    """
    Parameters:

        config (ConfigParser): The .halfapi/config based configparser object

    Returns:

        dict[str, ModuleType]
    """
    if not config.has_section('domains'):
        return {}

    try:
        sys.path.append('.')
        return {
            domain: importlib.import_module(''.join((domain, module)))
            for domain, module in config.items('domains')
        }
    except ImportError as exc:
        logger.error('Could not load a domain : %s', exc)
        raise exc

def router_acls(route_params: Dict, path: List, m_router: ModuleType) -> Generator:
    d_res = {'fqtn': route_params.get('FQTN')}

    for verb in VERBS:
        params = route_params.get(verb)
        if params is None:
            continue
        if len(params) == 0:
            logger.error('No ACL for route [{%s}] %s', verb, "/".join(path))
        else:
            for param in params:
                acl = param.get('acl')
                if not isinstance(acl, FunctionType):
                    continue

                yield acl.__name__, acl


def domain_acls(m_router, path):
    if not hasattr(m_router, 'ROUTES'):
        logger.error('Missing *ROUTES* constant in *%s*', m_router.__name__)
        raise Exception(f'No ROUTES constant for {m_router.__name__}')


    routes = m_router.ROUTES

    for subpath, route_params in routes.items():
        path.append(subpath)

        yield from router_acls(route_params, path, m_router)

        subroutes = route_params.get('SUBROUTES', [])
        for subroute in subroutes:
            logger.debug('Processing subroute **%s** - %s', subroute, m_router.__name__)
            path.append(subroute)
            try:
                submod = importlib.import_module(f'.{subroute}', m_router.__name__)
            except ImportError as exc:
                logger.error('Failed to import subroute **{%s}**', subroute)
                raise exc

            yield from domain_acls(submod, path)

            path.pop()

        path.pop()
