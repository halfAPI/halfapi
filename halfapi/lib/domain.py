#!/usr/bin/env python3
"""
lib/domain.py The domain-scoped utility functions
"""

import re
import sys
import importlib
import inspect
from functools import wraps
from types import ModuleType, FunctionType
from typing import Coroutine, Generator
from typing import Dict, List, Tuple
import yaml

from starlette.exceptions import HTTPException

from halfapi.lib import acl
from halfapi.lib.responses import ORJSONResponse, ODSResponse, XLSXResponse, PlainTextResponse, HTMLResponse
# from halfapi.lib.router import read_router
from halfapi.lib.constants import VERBS

from ..logging import logger

class MissingAclError(Exception):
    """ Exception to use when no acl are specified for a route
    """
    pass

class PathError(Exception):
    """ Exception to use when the path for a route is malformed
    """
    pass

class UnknownPathParameterType(Exception):
    """ Exception to use when the path parameter for a route is not supported
    """
    pass

class UndefinedRoute(Exception):
    """ Exception to use when the route definition cannot be found
    """
    pass

class UndefinedFunction(Exception):
    """ Exception to use when a function definition cannot be found
    """
    pass

class NoDomainsException(Exception):
    """ The exception that is raised when HalfAPI is called without domains
    """
    pass

def route_decorator(fct: FunctionType) -> Coroutine:
    """ Returns an async function that can be mounted on a router
    """
    @wraps(fct)
    @acl.args_check
    async def wrapped(request, *args, **kwargs):
        fct_args_spec = inspect.getfullargspec(fct).args
        fct_args_defaults = inspect.getfullargspec(fct).defaults or []
        fct_args_defaults_dict = dict(list(zip(
            reversed(fct_args_spec),
            reversed(fct_args_defaults)
        )))

        fct_args = request.path_params.copy()

        if 'halfapi' in fct_args_spec:
            fct_args['halfapi'] = {
                'user': request.user if
                    'user' in request else None,
                'config': request.scope.get('config', {}),
                'domain': request.scope.get('domain', 'unknown'),
            }


        if 'data' in fct_args_spec:
            if 'data' in fct_args_defaults_dict:
                fct_args['data'] = fct_args_defaults_dict['data']
            else:
                fct_args['data'] = {}

            fct_args['data'].update(kwargs.get('data', {}))

        if 'out' in fct_args_spec:
            fct_args['out'] = kwargs.get('out')

        """ If format argument is specified (either by get, post param or function argument)
        """
        if 'ret_type' in fct_args_defaults_dict:
            ret_type = fct_args_defaults_dict['ret_type']
        else:
            ret_type = fct_args.get('data', {}).get('format', 'json')

        logger.debug('Return type {} (defaults: {})'.format(ret_type,
            fct_args_defaults_dict))
        try:
            if ret_type == 'json':
                return ORJSONResponse(fct(**fct_args))

            if ret_type == 'ods':
                res = fct(**fct_args)
                assert isinstance(res, list)
                for elt in res:
                    assert isinstance(elt, dict)

                return ODSResponse(res)

            if ret_type == 'xlsx':
                res = fct(**fct_args)
                assert isinstance(res, list)
                for elt in res:
                    assert isinstance(elt, dict)

                return XLSXResponse(res)

            if ret_type in ['html', 'xhtml']:
                res = fct(**fct_args)
                assert isinstance(res, str)

                return HTMLResponse(res)

            if ret_type in 'txt':
                res = fct(**fct_args)
                assert isinstance(res, str)

                return PlainTextResponse(res)


            raise NotImplementedError

        except NotImplementedError as exc:
            raise HTTPException(501) from exc
        except Exception as exc:
            # TODO: Write tests
            logger.error(exc, exc_info=True)
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

