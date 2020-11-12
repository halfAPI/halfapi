#!/usr/bin/env python3
"""
app.py is the file that is read when launching the application using an asgi
runner.

It defines the following globals :

    - routes (contains the Route objects for the application)
    - application (the asgi application itself - a starlette object)

"""
import logging

# asgi framework
from starlette.applications import Starlette
from starlette.authentication import UnauthenticatedUser
from starlette.middleware import Middleware
from starlette.routing import Route
from starlette.middleware.authentication import AuthenticationMiddleware


# module libraries
from halfapi.conf import config, SECRET, PRODUCTION, DOMAINSDICT

from .lib.domain_middleware import DomainMiddleware

from halfapi.lib.jwt_middleware import JWTAuthenticationBackend

from halfapi.lib.responses import (ORJSONResponse, UnauthorizedResponse,
    NotFoundResponse, InternalServerErrorResponse, NotImplementedResponse)

from halfapi.lib.routes import gen_starlette_routes, api_routes, debug_routes
from halfapi.lib.schemas import get_api_routes, schema_json, get_acls

logger = logging.getLogger('uvicorn.asgi')

routes = [ Route('/', get_api_routes) ]


routes += [
    Route('/halfapi/current_user', lambda request, *args, **kwargs:
        ORJSONResponse({'user':request.user.json})
        if not isinstance(request.user, UnauthenticatedUser)
        else ORJSONResponse({'user': None})),
    Route('/halfapi/schema', schema_json),
    Route('/halfapi/acls', get_acls)
]

if not PRODUCTION:
    for route in debug_routes():
        routes.append( route )


for route in gen_starlette_routes(DOMAINSDICT()):
    routes.append(route)


application = Starlette(
    debug=not PRODUCTION,
    routes=routes,
    middleware=[
        Middleware(DomainMiddleware, config=config),
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
