from .routes import gen_starlette_routes
from .responses import *
from starlette.schemas import SchemaGenerator
schemas = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "HalfAPI", "version": "1.0"}}
)


async def schema_json(request, *args, **kwargs):
    return ORJSONResponse(
        schemas.get_schema(routes=request.app.routes))


def schema_dict_dom(m_domain):
    return schemas.get_schema(routes=[
        elt for elt in gen_starlette_routes(m_domain) ])
