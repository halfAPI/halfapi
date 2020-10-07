from types import ModuleType
from typing import Dict
from ..conf import DOMAINSDICT
from .routes import gen_starlette_routes
from .responses import *
from .jwt_middleware import UnauthenticatedUser, JWTUser
from starlette.schemas import SchemaGenerator
from starlette.routing import Router
SCHEMAS = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "HalfAPI", "version": "1.0"}}
)

"""
example: > {
"dummy_domain": {
    "/abc/alphabet/organigramme": {
        "fqtn": null,
        "params": [
            {}
        ],
        "verb": "GET"
    },
    "/act/personne/": {
        "fqtn": "acteur.personne",
        "params": [
            {}

        "verb": "GET"
    }

}
}
"""

async def get_api_routes(request, *args, **kwargs):
    """
     responses:
        200:
            description: Returns the current API routes description (HalfAPI 0.2.1)
                         as a JSON object 
    """
    assert 'api' in request.scope
    return ORJSONResponse(request.scope['api'])


async def schema_json(request, *args, **kwargs):
    """
    responses:
        200:
            description: Returns the current API routes description (OpenAPI v3)
                         as a JSON object
    """
    return ORJSONResponse(
        SCHEMAS.get_schema(routes=request.app.routes))


def schema_dict_dom(d_domains) -> Dict:
    """
    Returns the API schema of the *m_domain* domain as a python dictionnary

    Parameters:
    
        m_domain (ModuleType): The module to scan for routes


    Returns:
    
        Dict: A dictionnary containing the description of the API using the
            | OpenAPI standard 
    """
    return SCHEMAS.get_schema(
            routes=list(gen_starlette_routes(d_domains)))


async def get_acls(request, *args, **kwargs):
    """
    responses:
        200:
            description: A dictionnary of the domains and their acls, with the
                result of the acls functions
    """

    from .routes import api_acls
    return ORJSONResponse(api_acls(request))

