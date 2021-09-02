#!/usr/bin/env python3
"""
lib/domain.py The domain-scoped utility functions
"""

import re
import sys
import importlib
import inspect
import logging
from types import ModuleType, FunctionType
from typing import Coroutine, Generator
from typing import Dict, List, Tuple, Iterator

from starlette.exceptions import HTTPException

from halfapi.lib import acl
from halfapi.lib.responses import ORJSONResponse
from halfapi.lib.router import read_router
from halfapi.lib.constants import VERBS

logger = logging.getLogger("uvicorn.asgi")

class MissingAclError(Exception):
    pass

class PathError(Exception):
    pass

class UnknownPathParameterType(Exception):
    pass

class UndefinedRoute(Exception):
    pass

class UndefinedFunction(Exception):
    pass

def route_decorator(fct: FunctionType, ret_type: str = 'json') -> Coroutine:
    """ Returns an async function that can be mounted on a router
    """
    if ret_type == 'json':
        @acl.args_check
        async def wrapped(request, *args, **kwargs):
            fct_args_spec = inspect.getfullargspec(fct).args
            fct_args = request.path_params.copy()

            if 'halfapi' in fct_args_spec:
                fct_args['halfapi'] = {
                    'user': request.user if
                        'user' in request else None,
                    'config': request.scope['config'],
                    'domain': request.scope['domain'],

                }


            if 'data' in fct_args_spec:
                fct_args['data'] = kwargs.get('data')

            try:
                return ORJSONResponse(fct(**fct_args))
            except NotImplementedError as exc:
                raise HTTPException(501) from exc
            except Exception as exc:
                # TODO: Write tests
                if not isinstance(exc, HTTPException):
                    raise HTTPException(500) from exc
                raise exc


    else:
        raise Exception('Return type not available')

    return wrapped


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

def gen_routes(m_router: ModuleType,
    verb: str,
    path: List[str],
    params: List[Dict]) -> Tuple[FunctionType, Dict]:
    """
    Returns a tuple of the function associatied to the verb and path arguments,
    and the dictionary of it's acls

    Parameters:
        - m_router (ModuleType): The module containing the function definition

        - verb (str): The HTTP verb for the route (GET, POST, ...)

        - path (List): The route path, as a list (each item being a level of
            deepness), from the lowest level (domain) to the highest

        - params (Dict): The acl list of the following format :
            [{'acl': Function, 'args': {'required': [], 'optional': []}}]


    Returns:

        (Function, Dict): The destination function and the acl dictionary

    """
    if len(params) == 0:
        raise MissingAclError('[{}] {}'.format(verb, '/'.join(path)))

    if len(path) == 0:
        logger.error('Empty path for [{%s}]', verb)
        raise PathError()

    fct_name = get_fct_name(verb, path[-1])
    if hasattr(m_router, fct_name):
        fct = getattr(m_router, fct_name)
    else:
        raise UndefinedFunction('{}.{}'.format(m_router.__name__, fct_name or ''))


    if not inspect.iscoroutinefunction(fct):
        return route_decorator(fct), params
    else:
        return fct, params


def gen_router_routes(m_router: ModuleType, path: List[str]) -> \
    Iterator[Tuple[str, str, Coroutine, List]]:
    """
    Recursive generatore that parses a router (or a subrouter)
    and yields from gen_routes

    Parameters:

        - m_router (ModuleType): The currently treated router module
        - path (List[str]): The current path stack

    Yields:

        (str, str, Coroutine, List): A tuple containing the path, verb,
            function and parameters of the route
    """

    for subpath, params in read_router(m_router).items():
        path.append(subpath)

        for verb in VERBS:
            if verb not in params:
                continue
            yield ('/'.join(filter(lambda x: len(x) > 0, path)),
                verb,
                *gen_routes(m_router, verb, path, params[verb])
            )

        for subroute in params.get('SUBROUTES', []):
            #logger.debug('Processing subroute **%s** - %s', subroute, m_router.__name__)
            param_match = re.fullmatch('^([A-Z_]+)_([a-z]+)$', subroute)
            if param_match is not None:
                try:
                    path.append('{{{}:{}}}'.format(
                        param_match.groups()[0].lower(),
                        param_match.groups()[1]))
                except AssertionError as exc:
                    raise UnknownPathParameterType(subroute) from exc
            else:
                path.append(subroute)

            try:
                yield from gen_router_routes(
                    importlib.import_module(f'.{subroute}', m_router.__name__),
                    path)

            except ImportError as exc:
                logger.error('Failed to import subroute **{%s}**', subroute)
                raise exc

            path.pop()

        path.pop()


def d_domains(config) -> Dict[str, ModuleType]:
    """
    Parameters:

        config (ConfigParser): The .halfapi/config based configparser object

    Returns:

        dict[str, ModuleType]
    """
    if not 'domains' in config:
        return {}

    try:
        sys.path.append('.')
        return {
            domain: importlib.import_module(''.join((domain, module)))
            for domain, module in config['domains'].items()
        }
    except ImportError as exc:
        logger.error('Could not load a domain : %s', exc)
        raise exc

def router_acls(route_params: Dict, path: List, m_router: ModuleType) -> Generator:
    for verb in VERBS:
        params = route_params.get(verb)
        if params is None:
            continue
        if len(params) == 0:
            logger.error('No ACL for route [{%s}] %s', verb, "/".join(path))
        else:
            for param in params:
                fct_acl = param.get('acl')
                if not isinstance(fct_acl, FunctionType):
                    continue

                yield fct_acl.__name__, fct_acl


def domain_acls(m_router, path):
    routes = read_router(m_router)

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
