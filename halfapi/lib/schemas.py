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
    from .. import app

    return ORJSONResponse(app.d_api)


async def schema_json(request, *args, **kwargs):
    """
    responses:
        200:
            description: Returns the current API routes description (OpenAPI v3)
                         as a JSON object
    """
    return ORJSONResponse(
        SCHEMAS.get_schema(routes=request.app.routes))


def schema_dict_dom(m_domain: ModuleType) -> Dict:
    """
    Returns the API schema of the *m_domain* domain as a python dictionnary

    Parameters:
    
        m_domain (ModuleType): The module to scan for routes


    Returns:
    
        Dict: A dictionnary containing the description of the API using the
            | OpenAPI standard 
    """
    routes = [
        elt for elt in gen_starlette_routes(m_domain) ]
    return SCHEMAS.get_schema(routes=routes)


async def get_acls(request, *args, **kwargs):
    """
    responses:
        200:
            description: A dictionnary of the domains and their acls, with the
                result of the acls functions
    """

    from .routes import api_acls
    return ORJSONResponse(api_acls(request))
