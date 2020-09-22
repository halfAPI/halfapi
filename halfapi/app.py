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
from halfapi.conf import HOST, PORT, DB_NAME, SECRET, PRODUCTION, DOMAINS

from halfapi.lib.jwt_middleware import JWTAuthenticationBackend

from halfapi.lib.responses import *
from halfapi.lib.routes import gen_starlette_routes


routes = [
    Route('/', lambda request, *args, **kwargs: PlainTextResponse('It Works!')),
    Route('/user', lambda request, *args, **kwargs:
        JSONResponse({'user':request.user.json})
        if type(request.user) != UnauthenticatedUser
        else JSONResponse({'user':False})),
    Route('/payload', lambda request, *args, **kwargs:
        JSONResponse({'payload':str(request.payload)}))
] if not PRODUCTION else []

for route in gen_starlette_routes():
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
