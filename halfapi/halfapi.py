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
import importlib
from datetime import datetime

# asgi framework
from starlette.applications import Starlette
from starlette.authentication import UnauthenticatedUser
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse
from starlette.middleware.authentication import AuthenticationMiddleware

from timing_asgi import TimingMiddleware
from timing_asgi.integrations import StarletteScopeToName

# module libraries

from .lib.constants import API_SCHEMA_DICT
from .lib.domain_middleware import DomainMiddleware
from .lib.timing import HTimingClient
from .lib.jwt_middleware import JWTAuthenticationBackend
from .lib.responses import (ORJSONResponse, UnauthorizedResponse,
    NotFoundResponse, InternalServerErrorResponse, NotImplementedResponse,
    ServiceUnavailableResponse)
from .lib.domain import domain_schema_dict, NoDomainsException, domain_schema
from .lib.routes import gen_domain_routes, gen_schema_routes, JSONRoute
from .lib.schemas import schema_json, get_acls
from .logging import logger, config_logging
from halfapi import __version__



class HalfAPI:
    def __init__(self, config,
        routes_dict=None):
        config_logging(logging.DEBUG)

        SECRET = config.get('secret')
        PRODUCTION = config.get('production', True)
        CONFIG = config.get('config', {})
        DRYRUN = config.get('dryrun', False)

        self.PRODUCTION = PRODUCTION
        self.CONFIG = CONFIG
        self.SECRET = SECRET

        self.__application = None


        """ HalfAPI routes (if not PRODUCTION, includes debug routes)
        """
        routes = []
        routes.append(
            Route('/', JSONRoute({}))
        )

        routes.append(
            Mount('/halfapi', routes=list(self.routes()))
        )

        if routes_dict:
            # Mount the routes from the routes_dict argument - domain-less mode
            logger.info('Domain-less mode : the given schema defines the activated routes')
            for route in gen_schema_routes(routes_dict):
                routes.append(route)
        else:
            """
            for route in gen_domain_routes(m_domain_router):
                routes.append(route)
            """
            pass

        startup_fcts = []

        if DRYRUN:
            startup_fcts.append(
                HalfAPI.wait_quit()
            )

        self.__application = Starlette(
            debug=not PRODUCTION,
            routes=routes,
            exception_handlers={
                401: UnauthorizedResponse,
                404: NotFoundResponse,
                500: InternalServerErrorResponse,
                501: NotImplementedResponse,
                503: ServiceUnavailableResponse
            },
            on_startup=startup_fcts
        )

        """
        self.__application.add_middleware(
            DomainMiddleware,
            domain=domain,
            config=CONFIG
        )
        """

        if SECRET:
            self.SECRET = SECRET
            self.__application.add_middleware(
                AuthenticationMiddleware,
                backend=JWTAuthenticationBackend(secret_key=SECRET)
            )

        if not PRODUCTION:
            self.__application.add_middleware(
                TimingMiddleware,
                client=HTimingClient(),
                metric_namer=StarletteScopeToName(prefix="halfapi",
                starlette_app=self.__application)
            )


    @property
    def version(self):
        return __version__

    async def version_async(self, request, *args, **kwargs):
        return Response(self.version)

    @property
    def application(self):
        return self.__application

    def routes(self):
        """ Halfapi default routes
        """

        async def get_user(request, *args, **kwargs):
            return ORJSONResponse({'user':request.user})

        yield Route('/whoami', get_user)
        yield Route('/schema', schema_json)
        yield Route('/acls', get_acls)
        yield Route('/version', self.version_async)
        """ Halfapi debug routes definition
        """
        if self.PRODUCTION:
            return

        """ Debug routes
        """
        async def debug_log(request: Request, *args, **kwargs):
            logger.debug('debuglog# %s', {datetime.now().isoformat()})
            logger.info('debuglog# %s', {datetime.now().isoformat()})
            logger.warning('debuglog# %s', {datetime.now().isoformat()})
            logger.error('debuglog# %s', {datetime.now().isoformat()})
            logger.critical('debuglog# %s', {datetime.now().isoformat()})
            return Response('')
        yield Route('/log', debug_log)

        async def error_code(request: Request, *args, **kwargs):
            code = request.path_params['code']
            raise HTTPException(code)

        yield Route('/error/{code:int}', error_code)

        async def exception(request: Request, *args, **kwargs):
            raise Exception('Test exception')

        yield Route('/exception', exception)

    @staticmethod
    def api_schema(domain):
        pass

    @staticmethod
    def wait_quit():
        """ sleeps 1 second and quits. used in dry-run mode
        """
        import time
        import sys
        time.sleep(1)
        sys.exit(0)
