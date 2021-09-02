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
import logging
from typing import Dict, Coroutine
from types import ModuleType

from starlette.schemas import SchemaGenerator

from .. import __version__
from .routes import gen_starlette_routes, api_routes, api_acls
from .responses import ORJSONResponse

logger = logging.getLogger('uvicorn.asgi')
SCHEMAS = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "HalfAPI", "version": __version__}}
)

def get_api_routes(domains: Dict[str, ModuleType]) -> Coroutine:
    """
    description: Returns the current API routes dictionary
                 as a JSON object
    example: {
        "dummy_domain": {
            "abc/alphabet": {
                "GET": [
                    {
                        "acl": "public"
                    }
                ]
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
    routes = {
        domain: api_routes(m_domain)[0]
        for domain, m_domain in domains.items()
    }

    async def wrapped(request, *args, **kwargs):
        return ORJSONResponse(routes)

    return wrapped


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
