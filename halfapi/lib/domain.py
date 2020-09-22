#!/usr/bin/env python3
import importlib
import typing as t

VERBS = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')

def get_fct_name(http_verb, path: t.List):
    """
    Returns the predictable name of the function for a route

    Parameters:
        - http_verb (str): The Route's HTTP method (GET, POST, ...)
        - path (str): A path beginning by '/' for the route

    Returns:
        str: The *unique* function name for a route and it's verb


    Examples:

        >>> get_fct_name('foo', 'bar')
        Traceback (most recent call last):
            ...
        Exception: Malformed path

        >>> get_fct_name('get', '/')
        'get_'

        >>> get_fct_name('GET', '/')
        'get_'

        >>> get_fct_name('POST', '/foo')
        'post_foo'

        >>> get_fct_name('POST', '/foo/bar')
        'post_foo_bar'

        >>> get_fct_name('DEL', '/foo/{boo}/{far}/bar')
        'del_foo_BOO_FAR_bar'

        >>> get_fct_name('DEL', '/foo/{boo:zoo}')
        'del_foo_BOO'
    """
    fct_name = [http_verb.lower()]
    for elt in path:
        if elt and elt[0] == '{':
            fct_name.append(elt[1:-1].split(':')[0].upper())
        else:
            fct_name.append(elt)

    return '_'.join(fct_name)

def gen_routes(route_params, path, m_router):
    for verb in VERBS:
        params = route_params.get(verb)
        if params is None:
            continue
        if not len(params):
            print(f'No ACL for route [{verb}] "/".join(path)')

        try:
            fct_name = get_fct_name(verb, [path[-1]])
            fct = getattr(m_router, fct_name)
        except AttributeError:
            print(f'{fct_name} is not defined in {m_router.__name__}')
            continue

        yield {
            'verb':verb,
            'path':f"/{'/'.join([ elt for elt in path if elt ])}", 
            'params':params,
            'fct': fct }


def gen_router_routes(m_router, path=[]):
    """
    [
        ('path', [acl], fct)
    ]
    """

    if not hasattr(m_router, 'ROUTES'):
        print(f'Missing *ROUTES* constant in *{m_router.__name__}*')

    routes = m_router.ROUTES

    pathlen = len(path)
    for subpath, route_params in routes.items():
        path.append(subpath)

        for route in gen_routes(route_params, path, m_router):
            yield route
        
        subroutes = route_params.get('SUBROUTES', [])
        for subroute in subroutes:
            path.append(subroute)
            submod = importlib.import_module(f'.{subroute}', m_router.__name__)
            for route_scan in gen_router_routes(submod, path):
                yield route_scan

            path.pop()

        if pathlen < len(path):
            path.pop()




def gen_domain_routes(domain):
    m_domain = importlib.import_module(domain)

    if not hasattr(m_domain, 'routers'):
        raise Exception(f'No *routers* module in *{domain}*')

    m_router = importlib.import_module('.routers', domain)

    return gen_router_routes(m_router, [domain])
