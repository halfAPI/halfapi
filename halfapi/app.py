#!/usr/bin/env python3
"""
app.py is the file that is read when launching the application using an asgi
runner.

It defines the following globals :

    - routes (contains the Route objects for the application)
    - application (the asgi application itself - a starlette object)

"""
import logging
import time

# asgi framework
from starlette.applications import Starlette
from starlette.authentication import UnauthenticatedUser
from starlette.middleware import Middleware
from starlette.routing import Route
from starlette.responses import Response, PlainTextResponse
from starlette.middleware.authentication import AuthenticationMiddleware

from timing_asgi import TimingMiddleware
from timing_asgi.integrations import StarletteScopeToName

# module libraries

from .lib.domain_middleware import DomainMiddleware
from .lib.timing import HTimingClient

from halfapi.lib.jwt_middleware import JWTAuthenticationBackend

from halfapi.lib.responses import (ORJSONResponse, UnauthorizedResponse,
    NotFoundResponse, InternalServerErrorResponse, NotImplementedResponse)

from halfapi.lib.routes import gen_starlette_routes, debug_routes
from halfapi.lib.schemas import get_api_routes, get_api_domain_routes, schema_json, get_acls
from halfapi.logging import logger, config_logging
from halfapi import __version__



class HalfAPI:
    def __init__(self, config=None):
        config_logging(logging.DEBUG)

        if config:
            SECRET = config.get('SECRET')
            PRODUCTION = config.get('PRODUCTION')
            DOMAINS = config.get('DOMAINS', {})
            CONFIG = config.get('CONFIG', {
                'domains': DOMAINS
            })
        else:
            from halfapi.conf import CONFIG, SECRET, PRODUCTION, DOMAINS


        routes = [ Route('/', get_api_routes(DOMAINS)) ]




        for route in self.routes():
            routes.append(route)

        if not PRODUCTION:
            for route in debug_routes():
                routes.append( route )


        if DOMAINS:
            for route in gen_starlette_routes(DOMAINS):
                routes.append(route)

            for domain, m_domain in DOMAINS.items():
                routes.append(
                    Route(
                        f'/{domain}',
                        get_api_domain_routes(m_domain)
                    )
                )


        self.application = Starlette(
            debug=not PRODUCTION,
            routes=routes,
            exception_handlers={
                401: UnauthorizedResponse,
                404: NotFoundResponse,
                500: InternalServerErrorResponse,
                501: NotImplementedResponse
            }
        )

        self.application.add_middleware(
            DomainMiddleware,
            config=CONFIG
        )

        if SECRET:
            self.SECRET = SECRET
            self.application.add_middleware(
                AuthenticationMiddleware,
                backend=JWTAuthenticationBackend(secret_key=SECRET)
            )

        if not PRODUCTION:
            self.application.add_middleware(
                TimingMiddleware,
                client=HTimingClient(),
                metric_namer=StarletteScopeToName(prefix="halfapi",
                starlette_app=self.application)
            )

        logger.info('CONFIG:\n%s', CONFIG)

    @property
    def version(self):
        return __version__

    async def version_async(self, request, *args, **kwargs):
        return Response(self.version)

    def routes(self):
        """ Halfapi default routes
        """

        async def get_user(request, *args, **kwargs):
            return ORJSONResponse({'user':request.user})

        yield Route('/halfapi/whoami', get_user)
        yield Route('/halfapi/schema', schema_json)
        yield Route('/halfapi/acls', get_acls)
        yield Route('/halfapi/version', self.version_async)

application = HalfAPI().application
