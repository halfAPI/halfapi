""" Schemas module

Functions :
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
from ..logging import logger
from .routes import api_routes
from .responses import ORJSONResponse

SCHEMAS = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "HalfAPI", "version": __version__}}
)

async def schema_json(request, *args, **kwargs):
    """
    description: Returns the current API routes description (OpenAPI v3)
                 as a JSON object
    """
    return ORJSONResponse(
        SCHEMAS.get_schema(routes=request.app.routes))


def schema_csv_dict(csv: List[str], prefix='/') -> Dict:
    package = None
    schema_d = {}

    modules_d = {}

    acl_modules_d = {}


    for line in csv:
        if not line:
            continue

        path, verb, router, acl_fct_name, args_req, args_opt, out = line.strip().split(';')
        logger.info('schema_csv_dict %s %s %s', path, args_req, args_opt)
        path = f'{prefix}{path}'

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
