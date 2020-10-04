#!/usr/bin/env python3
import importlib
from types import ModuleType
from typing import Generator, Dict, List

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
    d_res = {'fqtn': route_params.get('FQTN')}

    for verb in VERBS:
        params = route_params.get(verb)
        if params is None:
            continue
        if len(params) == 0:
            print(f'No ACL for route [{verb}] "/".join(path)')

        try:
            fct_name = get_fct_name(verb, path[-1])
            fct = getattr(m_router, fct_name)
        except AttributeError:
            print(f'{fct_name} is not defined in {m_router.__name__}')
            continue

        d_res[verb] = {'fct': fct, 'params': params}

    yield f"/{'/'.join([ elt for elt in path if elt ])}", d_res


def gen_router_routes(m_router, path=None):
    """
    {
        '/truc/toto': {
        }
    }
    """

    if not hasattr(m_router, 'ROUTES'):
        print(f'Missing *ROUTES* constant in *{m_router.__name__}*')

    if path is None:
        path = []

    routes = m_router.ROUTES

    for subpath, route_params in routes.items():
        path.append(subpath)

        yield from gen_routes(route_params, path, m_router)

        subroutes = route_params.get('SUBROUTES', [])
        for subroute in subroutes:
            path.append(subroute)
            submod = importlib.import_module(f'.{subroute}', m_router.__name__)
            yield from gen_router_routes(submod, path)

            path.pop()

        path.pop()



def gen_domain_routes(domain):
    m_router = importlib.import_module('.routers', domain)

    return gen_router_routes(m_router, [domain])
