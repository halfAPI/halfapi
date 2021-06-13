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
from starlette.routing import Route
from starlette.middleware.authentication import AuthenticationMiddleware

from timing_asgi import TimingMiddleware
from timing_asgi.integrations import StarletteScopeToName

# module libraries
from halfapi.conf import config, SECRET, PRODUCTION, DOMAINSDICT

from .lib.domain_middleware import DomainMiddleware
from .lib.timing import HTimingClient

from halfapi.lib.jwt_middleware import JWTAuthenticationBackend

from halfapi.lib.responses import (ORJSONResponse, UnauthorizedResponse,
    NotFoundResponse, InternalServerErrorResponse, NotImplementedResponse)

from halfapi.lib.routes import gen_starlette_routes, debug_routes
from halfapi.lib.schemas import get_api_routes, schema_json, get_acls

logger = logging.getLogger('uvicorn.asgi')

routes = [ Route('/', get_api_routes) ]


routes += [
    Route('/halfapi/schema', schema_json),
    Route('/halfapi/acls', get_acls)
]

routes += Route('/halfapi/current_user', lambda request, *args, **kwargs:
    ORJSONResponse({'user':request.user.json})
    if SECRET and not isinstance(request.user, UnauthenticatedUser)
    else ORJSONResponse({'user': None})),


if not PRODUCTION:
    for route in debug_routes():
        routes.append( route )


if DOMAINSDICT:
    for route in gen_starlette_routes(DOMAINSDICT()):
        routes.append(route)


application = Starlette(
    debug=not PRODUCTION,
    routes=routes,
    exception_handlers={
        401: UnauthorizedResponse,
        404: NotFoundResponse,
        500: InternalServerErrorResponse,
        501: NotImplementedResponse
    }
)

if DOMAINSDICT:
    application.add_middleware(
        DomainMiddleware,
        config=config
    )

if SECRET:
    application.add_middleware(
        AuthenticationMiddleware,
        backend=JWTAuthenticationBackend(secret_key=SECRET)
    )

if not PRODUCTION:
    application.add_middleware(
        TimingMiddleware,
        client=HTimingClient(),
        metric_namer=StarletteScopeToName(prefix="halfapi",
        starlette_app=application)
    )
