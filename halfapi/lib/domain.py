#!/usr/bin/env python3
"""
lib/domain.py The domain-scoped utility functions
"""

import os
import re
import sys
import importlib
import inspect
from functools import wraps
from types import ModuleType, FunctionType
from typing import Coroutine, Generator
from typing import Dict, List, Tuple, Iterator
import yaml

from starlette.exceptions import HTTPException

from halfapi.lib import acl
from halfapi.lib.responses import ORJSONResponse, ODSResponse
# from halfapi.lib.router import read_router
from halfapi.lib.constants import VERBS

from ..logging import logger

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

class NoDomainsException(Exception):
    """ The exception that is raised when HalfAPI is called without domains
    """
    pass

def route_decorator(fct: FunctionType, ret_type: str = 'json') -> Coroutine:
    """ Returns an async function that can be mounted on a router
    """
    @wraps(fct)
    @acl.args_check
    async def wrapped(request, *args, **kwargs):
        fct_args_spec = inspect.getfullargspec(fct).args
        fct_args = request.path_params.copy()

        if 'halfapi' in fct_args_spec:
            fct_args['halfapi'] = {
                'user': request.user if
                    'user' in request else None,
                'config': request.scope.get('config', {}),
                'domain': request.scope.get('domain', 'unknown'),
            }


        if 'data' in fct_args_spec:
            fct_args['data'] = kwargs.get('data')

        """ If format argument is specified (either by get or by post param)
        """
        ret_type = fct_args.get('data', {}).get('format', 'json')

        try:
            if ret_type == 'json':
                return ORJSONResponse(fct(**fct_args))
            elif ret_type == 'ods':
                res = fct(**fct_args)
                assert isinstance(res, list)
                for elt in res:
                    assert isinstance(elt, dict)

                return ODSResponse(res)
            else:
                raise NotImplementedError
        except NotImplementedError as exc:
            raise HTTPException(501) from exc
        except Exception as exc:
            # TODO: Write tests
            if not isinstance(exc, HTTPException):
                raise HTTPException(500) from exc
            raise exc

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
        return acl.args_check(fct), params


# def gen_router_routes(m_router: ModuleType, path: List[str]) -> \
#     Iterator[Tuple[str, str, ModuleType, Coroutine, List]]:
#     """
#     Recursive generator that parses a router (or a subrouter)
#     and yields from gen_routes
# 
#     Parameters:
# 
#         - m_router (ModuleType): The currently treated router module
#         - path (List[str]): The current path stack
# 
#     Yields:
# 
#         (str, str, ModuleType, Coroutine, List): A tuple containing the path, verb,
#             router module, function reference and parameters of the route.
#             Function and parameters are yielded from then gen_routes function,
#             that decorates the endpoint function.
#     """
# 
#     for subpath, params in read_router(m_router).items():
#         path.append(subpath)
# 
#         for verb in VERBS:
#             if verb not in params:
#                 continue
#             yield ('/'.join(filter(lambda x: len(x) > 0, path)),
#                 verb,
#                 m_router,
#                 *gen_routes(m_router, verb, path, params[verb])
#             )
# 
#         for subroute in params.get('SUBROUTES', []):
#             #logger.debug('Processing subroute **%s** - %s', subroute, m_router.__name__)
#             param_match = re.fullmatch('^([A-Z_]+)_([a-z]+)$', subroute)
#             if param_match is not None:
#                 try:
#                     path.append('{{{}:{}}}'.format(
#                         param_match.groups()[0].lower(),
#                         param_match.groups()[1]))
#                 except AssertionError as exc:
#                     raise UnknownPathParameterType(subroute) from exc
#             else:
#                 path.append(subroute)
# 
#             try:
#                 yield from gen_router_routes(
#                     importlib.import_module(f'.{subroute}', m_router.__name__),
#                     path)
# 
#             except ImportError as exc:
#                 logger.error('Failed to import subroute **{%s}**', subroute)
#                 raise exc
# 
#             path.pop()
# 
#         path.pop()
# 


# def domain_schema_dict(m_router: ModuleType) -> Dict:
#     """ gen_router_routes return values as a dict
#     Parameters:
# 
#        m_router (ModuleType): The domain routers' module
# 
#     Returns:
# 
#        Dict: Schema of dict is halfapi.lib.constants.DOMAIN_SCHEMA
# 
#     @TODO: Should be a "router_schema_dict" function
#     """
#     d_res = {}
# 
#     for path, verb, m_router, fct, parameters in gen_router_routes(m_router, []):
#         if path not in d_res:
#             d_res[path] = {}
# 
#         if verb not in d_res[path]:
#             d_res[path][verb] = {}
# 
#         d_res[path][verb]['callable'] = f'{m_router.__name__}:{fct.__name__}'
#         try:
#             d_res[path][verb]['docs'] = yaml.safe_load(fct.__doc__)
#         except AttributeError:
#             logger.error(
#                 'Cannot read docstring from fct (fct=%s path=%s verb=%s', fct.__name__, path, verb)
# 
#         d_res[path][verb]['acls'] = list(map(lambda elt: { **elt, 'acl': elt['acl'].__name__ },
#             parameters))
# 
#     return d_res

from .constants import API_SCHEMA_DICT
def domain_schema(m_domain: ModuleType) -> Dict:
    schema = { **API_SCHEMA_DICT }
    routers_submod_str = getattr(m_domain, '__routers__', '.routers')
    m_domain_acl = importlib.import_module('.acl', m_domain.__package__)
    m_domain_routers = importlib.import_module(
        routers_submod_str, m_domain.__package__
    )
    schema['domain'] = {
        'name': getattr(m_domain, '__name__'),
        'version': getattr(m_domain, '__version__', ''),
        'patch_release': getattr(m_domain, '__patch_release__', ''),
        'routers': routers_submod_str,
        'acls': tuple(getattr(m_domain_acl, 'ACLS', ()))
    }
    schema['paths'] = domain_schema_dict(m_domain_routers)
    return schema

def domain_schema_list(m_router: ModuleType) -> List:
    """ Schema as list, one row by route/acl
    Parameters:

       m_router (ModuleType): The domain routers' module

    Returns:

       List[Tuple]: (path, verb, callable, doc, acls)
    """
    res = []

    for path, verb, m_router, fct, parameters in gen_router_routes(m_router, []):
        for params in parameters:
            res.append((
                path,
                verb,
                f'{m_router.__name__}:{fct.__name__}',
                params.get('acl').__name__,
                params.get('args', {}).get('required', []),
                params.get('args', {}).get('optional', []),
                params.get('out', [])
            ))

    return res



def d_domains(config) -> Dict[str, ModuleType]:
    """
    Parameters:

        config (ConfigParser): The .halfapi/config based configparser object

    Returns:

        dict[str, ModuleType]
    """

    domains = {}

    if os.environ.get('HALFAPI_DOMAIN_NAME') and os.environ.get('HALFAPI_DOMAIN_MODULE', '.routers'):
        domains[os.environ.get('HALFAPI_DOMAIN_NAME')] = os.environ.get('HALFAPI_DOMAIN_MODULE')
    elif 'domains' in config:
        domains = dict(config['domains'].items())

    try:
        return {
            domain: importlib.import_module(''.join((domain, module)))
            for domain, module in domains.items()
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
