#!/usr/bin/env python3
"""
Routes module

Fonctions :
    - route_acl_decorator
    - gen_starlette_routes
    - api_routes
    - api_acls
    - debug_routes

Exception :
    - DomainNotFoundError

"""
from datetime import datetime
from functools import partial, wraps
import logging
from typing import Callable, List, Dict, Generator, Tuple
from types import ModuleType, FunctionType

from starlette.exceptions import HTTPException
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse

from halfapi.lib.domain import gen_router_routes, domain_acls
from ..conf import DOMAINSDICT


logger = logging.getLogger('uvicorn.asgi')

class DomainNotFoundError(Exception):
    """ Exception when a domain is not importable
    """

def route_acl_decorator(fct: Callable = None, params: List[Dict] = None):
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

    if not params:
        params = []

    if not fct:
        return partial(route_acl_decorator, params=params)


    @wraps(fct)
    async def caller(req: Request, *args, **kwargs):
        for param in params:
            if param.get('acl'):
                passed = param['acl'](req, *args, **kwargs)
                if isinstance(passed, FunctionType):
                    passed = param['acl']()(req, *args, **kwargs)

                if not passed:
                    logger.debug(
                        'ACL FAIL for current route (%s - %s)', fct, param.get('acl'))
                    continue

                logger.debug(
                    'ACL OK for current route (%s - %s)', fct, param.get('acl'))

                req.scope['acl_pass'] = param['acl'].__name__
                if 'args' in param:
                    req.scope['args'] = param['args']

                if 'check' in req.query_params:
                    return PlainTextResponse(param['acl'].__name__)

                return await fct(
                    req, *args,
                    **{
                        **kwargs,
                        **param
                    })

        if 'check' in req.query_params:
            return PlainTextResponse('')

        raise HTTPException(401)

    return caller


def gen_starlette_routes(d_domains: Dict[str, ModuleType]) -> Generator:
    """
    Yields the Route objects for HalfAPI app

    Parameters:
        d_domains (dict[str, ModuleType])

    Returns:
        Generator(Route)
    """

    for domain_name, m_domain in d_domains.items():
        for path, verb, fct, params in gen_router_routes(m_domain, []):
            yield (
                Route(f'/{domain_name}/{path}',
                    route_acl_decorator(
                        fct,
                        params
                    ),
                    methods=[verb])
            )



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
    for path, verb, _, params in gen_router_routes(m_dom, []):
        if path not in d_res:
            d_res[path] = {}
        d_res[path][verb] = str_acl(params)

    return d_res, d_acls


def api_acls(request):
    """ Returns the list of possible ACLs
    """
    res = {}
    domains = DOMAINSDICT()
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


def debug_routes():
    """ Halfapi debug routes definition
    """
    async def debug_log(request: Request, *args, **kwargs):
        logger.debug('debuglog# %s', {datetime.now().isoformat()})
        logger.info('debuglog# %s', {datetime.now().isoformat()})
        logger.warning('debuglog# %s', {datetime.now().isoformat()})
        logger.error('debuglog# %s', {datetime.now().isoformat()})
        logger.critical('debuglog# %s', {datetime.now().isoformat()})
        return Response('')
    yield Route('/halfapi/log', debug_log)

    async def error_code(request: Request, *args, **kwargs):
        code = request.path_params['code']
        raise HTTPException(code)

    yield Route('/halfapi/error/{code:int}', error_code)

    async def exception(request: Request, *args, **kwargs):
        raise Exception('Test exception')

    yield Route('/halfapi/exception', exception)
