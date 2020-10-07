#!/usr/bin/env python3
from functools import wraps
from typing import Callable, List, Dict, Generator
from types import ModuleType, FunctionType

from starlette.exceptions import HTTPException
from starlette.routing import Route
from starlette.requests import Request

from halfapi.lib.domain import gen_domain_routes, VERBS

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
            if param.get('acl'):
                passed = param['acl'](req, *args, **kwargs)
                if isinstance(passed, FunctionType):
                    passed = param['acl']()(req, *args, **kwargs)

                if not passed:
                    continue

                return await fct(
                    req, *args,
                    **{
                        **kwargs,
                        **param
                    })

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
        for path, d_route in gen_domain_routes(domain_name, m_domain):
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

    d_acls = {}

    def str_acl(params):
        l_params = []

        for param in params:
            if 'acl' not in param.keys():
                continue

            l_params.append(param.copy())
            l_params[-1]['acl'] = param['acl'].__name__

            if param['acl'] not in d_acls.keys():
                d_acls[param['acl'].__name__] = param['acl']

        return l_params

    d_res = {}
    for path, d_route in gen_domain_routes(m_dom.__name__, m_dom):
        d_res[path] = {'fqtn': d_route['fqtn'] }

        for verb in VERBS:
            if verb not in d_route.keys():
                continue
            d_res[path][verb] = str_acl(d_route[verb]['params'])

    return d_res, d_acls


def api_acls(request):
    res = {}
    for domain, d_domain_acl in request.scope['acl'].items():
        res[domain] = {}
        for acl_name, fct in d_domain_acl.items():
            fct_result = fct(request)
            if isinstance(fct_result, FunctionType):
                fct_result = fct()(request)
            res[domain][acl_name] = fct_result

    return res
