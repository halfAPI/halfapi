#!/usr/bin/env python3
# asgi framework
from starlette.applications import Starlette
from starlette.authentication import UnauthenticatedUser
from starlette.middleware import Middleware
from starlette.responses import Response, JSONResponse
from starlette.routing import Route
from starlette.middleware.authentication import AuthenticationMiddleware

# typing
from typing import Any, Awaitable, Callable, MutableMapping

# module libraries
from halfapi.conf import HOST, PORT, DB_NAME, SECRET, PRODUCTION, DOMAINS, DOMAINSDICT

from halfapi.lib.jwt_middleware import JWTAuthenticationBackend

from halfapi.lib.responses import *
from halfapi.lib.routes import gen_starlette_routes, api_routes
from halfapi.lib.schemas import get_api_routes, schema_json, get_acls


"""
Base routes definition

Only debug or doc routes, that should not be available in production
"""
routes = [ Route('/', get_api_routes) ]


routes += [
    Route('/halfapi/current_user', lambda request, *args, **kwargs:
        ORJSONResponse({'user':request.user.json})
        if type(request.user) != UnauthenticatedUser
        else ORJSONResponse({'user': None})),
    Route('/halfapi/schema', schema_json),
    Route('/halfapi/acls', get_acls)
]

for domain, m_domain in DOMAINSDICT.items():
    for route in gen_starlette_routes(m_domain):
        routes.append(route)


d_api = {}
d_acl = {}
for domain, m_domain in DOMAINSDICT.items():
    d_api[domain], d_acl[domain] = api_routes(m_domain)


application = Starlette(
    debug=not PRODUCTION,
    routes=routes,
    middleware=[
        Middleware(AuthenticationMiddleware,
            backend=JWTAuthenticationBackend(secret_key=SECRET))
    ],
    exception_handlers={
        401: UnauthorizedResponse,
        404: NotFoundResponse,
        500: InternalServerErrorResponse,
        501: NotImplementedResponse
    }
)
