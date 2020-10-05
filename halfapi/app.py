#!/usr/bin/env python3
"""
app.py is the file that is read when launching the application using an asgi
runner.

It defines the following globals :

    - routes (contains the Route objects for the application)
    - d_acl (a dictionnary of the active acls for the current project)
    - d_api (a dictionnary of the routes depending on the routers definition in
      the project)
    - application (the asgi application itself - a starlette object)

"""
# asgi framework
from starlette.applications import Starlette
from starlette.authentication import UnauthenticatedUser
from starlette.middleware import Middleware
from starlette.routing import Route
from starlette.middleware.authentication import AuthenticationMiddleware


# module libraries
from halfapi.conf import SECRET, PRODUCTION, DOMAINSDICT

from halfapi.lib.jwt_middleware import JWTAuthenticationBackend

from halfapi.lib.responses import (ORJSONResponse, UnauthorizedResponse,
    NotFoundResponse, InternalServerErrorResponse, NotImplementedResponse)

from halfapi.lib.routes import gen_starlette_routes, api_routes
from halfapi.lib.schemas import get_api_routes, schema_json, get_acls


routes = [ Route('/', get_api_routes) ]


routes += [
    Route('/halfapi/current_user', lambda request, *args, **kwargs:
        ORJSONResponse({'user':request.user.json})
        if not isinstance(request.user, UnauthenticatedUser)
        else ORJSONResponse({'user': None})),
    Route('/halfapi/schema', schema_json),
    Route('/halfapi/acls', get_acls)
]

d_api = {}
d_acl = {}

for domain, m_domain in DOMAINSDICT.items():
    for route in gen_starlette_routes(m_domain):
        routes.append(route)

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
