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
from halfapi.lib.routes import gen_starlette_routes
from halfapi.lib.schemas import sch_json


"""
Base routes definition

Only debug or doc routes, that should not be available in production
"""
routes = [
    Route('/', lambda request, *args, **kwargs: ORJSONResponse('It Works!')),

    Route('/user', lambda request, *args, **kwargs:
        ORJSONResponse({'user':request.user.json})
        if type(request.user) != UnauthenticatedUser
        else ORJSONResponse({'user':False})),

    Route('/payload', lambda request, *args, **kwargs:
        ORJSONResponse({'payload':str(request.payload)})),

    Route('/schema', schema_json)
] if not PRODUCTION else []

for domain, m_domain in DOMAINSDICT.items():
    for route in gen_starlette_routes(m_dom):
        routes.append(route)


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
