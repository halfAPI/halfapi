from types import ModuleType
from typing import Dict
from ..conf import DOMAINSDICT
from .routes import gen_starlette_routes, api_routes
from .responses import *
from starlette.schemas import SchemaGenerator
from starlette.routing import Router
schemas = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "HalfAPI", "version": "1.0"}}
)


async def get_api_routes(request, *args, **kwargs):
    """
     responses:
        200:
            description: Returns the current API routes description (HalfAPI 0.2.1)
                         as a JSON object 
            example:
                {
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
    #TODO: LADOC
    d_api = {}
    for domain, m_domain in DOMAINSDICT.items():
        d_api[domain] = api_routes(m_domain)
    return ORJSONResponse(d_api)


async def schema_json(request, *args, **kwargs):
    """
    responses:
        200:
            description: Returns the current API routes description (OpenAPI v3)
                         as a JSON object
    """
    return ORJSONResponse(
        schemas.get_schema(routes=request.app.routes))


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
    return schemas.get_schema(routes=routes)
