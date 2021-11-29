""" Schemas module

Functions :
    - get_api_routes
    - schema_json
    - schema_dict_dom
    - get_acls

Constant :
    SCHEMAS (starlette.schemas.SchemaGenerator)
"""

import os
import importlib
from typing import Dict, Coroutine, List
from types import ModuleType

from starlette.schemas import SchemaGenerator

from .. import __version__
from .domain import gen_router_routes
from ..logging import logger
from .routes import gen_starlette_routes, api_routes, api_acls
from .responses import ORJSONResponse

SCHEMAS = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "HalfAPI", "version": __version__}}
)

def get_api_routes(domains: Dict[str, ModuleType]) -> Dict:
    """
    description: Returns the current API routes dictionary
                 as a JSON object
    example: {
        "dummy_domain": {
            "abc/alphabet": {
                "GET": {
                    "docs": "",
                    "acls": [
                        {
                            "acl": "public"
                        }
                    ]
                }
            },
            "abc/alphabet/{test:uuid}": {
                "GET": [
                    {
                        "acl": "public"
                    }
                ],
                "POST": [
                    {
                        "acl": "public"
                    }
                ],
                "PATCH": [
                    {
                        "acl": "public"
                    }
                ],
                "PUT": [
                    {
                        "acl": "public"
                    }
                ]
            }
        }
    }
    """
    return {
        domain: api_routes(m_domain)[0]
        for domain, m_domain in domains.items()
    }


def get_api_domain_routes(m_domain: ModuleType) -> Coroutine:
    routes, _ = api_routes(m_domain)

    async def wrapped(request, *args, **kwargs):
        """
        description: Returns the current API routes dictionary for a specific
            domain as a JSON object
        """
        return ORJSONResponse(routes)

    return wrapped



async def schema_json(request, *args, **kwargs):
    """
    description: Returns the current API routes description (OpenAPI v3)
                 as a JSON object
    """
    return ORJSONResponse(
        SCHEMAS.get_schema(routes=request.app.routes))


def schema_dict_dom(d_domains: Dict[str, ModuleType]) -> Dict:
    """
    Returns the API schema of the *m_domain* domain as a python dictionnary

    Parameters:

    d_domains (Dict[str, moduleType]): The module to scan for routes

    Returns:

        Dict: A dictionnary containing the description of the API using the
            | OpenAPI standard
    """
    return SCHEMAS.get_schema(
            routes=list(gen_starlette_routes(d_domains)))


async def get_acls(request, *args, **kwargs):
    """
    description: A dictionnary of the domains and their acls, with the
                 result of the acls functions
    """
    return ORJSONResponse(api_acls(request))


def schema_to_csv(module_name, header=True) -> str:
    """
    Returns a string composed where each line is a set of path, verb, function,
    acl, required arguments, optional arguments and output variables. Those
    lines should be unique in the result string;
    """
    # retrieve module
    mod = importlib.import_module(module_name)
    lines = []
    if header:
        lines.append([
            'path',
            'method',
            'module:function',
            'acl',
            'args_required', 'args_optional',
            'out'
        ])


    for path, verb, m_router, fct, parameters in gen_router_routes(mod, []):
        """ Call route generator (.lib.domain)
        """

        for param in parameters:
            """ Each parameters row represents rules for a specific ACL
            """
            fields = (
                f'/{path}',
                verb,
                f'{m_router.__name__}:{fct.__name__}',
                param['acl'].__name__,
                ','.join((param.get('args', {}).get('required', set()))),
                ','.join((param.get('args', {}).get('optional', set()))),
                ','.join((param.get('out', set())))
            )

            if fields[0:4] in map(lambda elt: elt[0:4], lines):
                raise Exception(
                    'Already defined acl for this route \
                    (path: {}, verb: {}, acl: {})'.format(
                        path,
                        verb,
                        param['acl'].__name__
                    )
                )

            lines.append(fields)

    return '\n'.join(
        [ ';'.join(fields) for fields in lines ]
    )



def schema_csv_dict(csv: List[str]) -> Dict:
    package = None
    schema_d = {}

    modules_d = {}

    acl_modules_d = {}


    for line in csv:
        path, verb, router, acl_fct_name, args_req, args_opt, out = line.strip().split(';')
        logger.info('schema_csv_dict %s %s %s', path, args_req, args_opt)
        if path not in schema_d:
            schema_d[path] = {}


        if verb not in schema_d[path]:
            mod_str = router.split(':')[0]
            fct_str = router.split(':')[1]

            if mod_str not in modules_d:
                modules_d[mod_str] = importlib.import_module(mod_str)

            if not hasattr(modules_d[mod_str], fct_str):
                raise Exception(
                    'Missing function in module. module:{} function:{}'.format(
                        router, fct_str
                    )
                )

            fct = getattr(modules_d[mod_str], fct_str)

            schema_d[path][verb] = {
                'module': modules_d[mod_str],
                'fct': fct,
                'acls': []
            }

        if package and router.split('.')[0] != package:
            raise Exception('Multi-domain is not allowed in that mode')

        package = router.split('.')[0]
        if not len(package):
            raise Exception(
                'Empty package name (router=%s)'.format(router))

        acl_package = f'{package}.acl'

        if acl_package not in acl_modules_d:
            if acl_package not in modules_d:
                modules_d[acl_package] = importlib.import_module(acl_package)
            if not hasattr(modules_d[acl_package], acl_fct_name):
                raise Exception(
                    'Missing acl function in module. module:{} acl:{}'.format(
                        acl_package, acl_fct_name
                    )
                )

            acl_modules_d[acl_package] = {}

        acl_modules_d[acl_package][acl_fct_name] = getattr(modules_d[acl_package], acl_fct_name)

        schema_d[path][verb]['acls'].append({
            'acl': acl_modules_d[acl_package][acl_fct_name],
            'args': {
                'required': set(args_req.split(',')) if len(args_req) else set(),
                'optional': set(args_opt.split(',')) if len(args_opt) else set()
            }
        })

    return schema_d
