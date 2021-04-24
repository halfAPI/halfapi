""" Schemas module

Functions :
    - get_api_routes
    - schema_json
    - schema_dict_dom
    - get_acls

Constant :
    SCHEMAS (starlette.schemas.SchemaGenerator)
"""

from typing import Dict

from starlette.schemas import SchemaGenerator

from .routes import gen_starlette_routes, api_acls
from .responses import ORJSONResponse

SCHEMAS = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "HalfAPI", "version": "1.0"}}
)

async def get_api_routes(request, *args, **kwargs):
    """
    description: Returns the current API routes description (HalfAPI 0.2.1)
                 as a JSON object
    """
    return ORJSONResponse(request.scope['api'])


async def schema_json(request, *args, **kwargs):
    """
    description: Returns the current API routes description (OpenAPI v3)
                 as a JSON object
    """
    return ORJSONResponse(
        SCHEMAS.get_schema(routes=request.app.routes))


def schema_dict_dom(d_domains) -> Dict:
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
