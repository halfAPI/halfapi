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

from .lib.domain_middleware import DomainMiddleware
from .lib.timing import HTimingClient
from .lib.domain import NoDomainsException

from halfapi.lib.jwt_middleware import JWTAuthenticationBackend

from halfapi.lib.responses import (ORJSONResponse, UnauthorizedResponse,
    NotFoundResponse, InternalServerErrorResponse, NotImplementedResponse,
    ServiceUnavailableResponse)

from halfapi.lib.routes import gen_domain_routes, gen_schema_routes, JSONRoute
from halfapi.lib.schemas import get_api_routes, get_api_domain_routes, schema_json, get_acls
from halfapi.logging import logger, config_logging
from halfapi import __version__



class HalfAPI:
    def __init__(self, config, routes_dict=None):
        config_logging(logging.DEBUG)

        SECRET = config.get('secret')
        PRODUCTION = config.get('production', True)
        DOMAINS = config.get('domains', {})
        CONFIG = config.get('config', {
            'domains': DOMAINS
        })

        if not (DOMAINS or routes_dict):
            raise NoDomainsException()

        self.PRODUCTION = PRODUCTION
        self.CONFIG = CONFIG
        self.DOMAINS = DOMAINS
        self.SECRET = SECRET

        self.__application = None

        """ The base route contains the route schema
        """
        if routes_dict:
            any_route = routes_dict[
                list(routes_dict.keys())[0]
            ]
            domain, router = any_route[
                list(any_route.keys())[0]
            ]['module'].__name__.split('.')[0:2]

            DOMAINS = {}
            DOMAINS[domain] = importlib.import_module(f'{domain}.{router}')

        if DOMAINS:
            self.api_routes = get_api_routes(DOMAINS)

        routes = [ Route('/', JSONRoute(self.api_routes)) ]

        """ HalfAPI routes (if not PRODUCTION, includes debug routes)
        """
        routes.append(
            Mount('/halfapi', routes=list(self.routes()))
        )

        if routes_dict:
            # Mount the routes from the routes_dict argument - domain-less mode
            logger.info('Domain-less mode : the given schema defines the activated routes')
            for route in gen_schema_routes(routes_dict):
                routes.append(route)
        elif DOMAINS:
            # Mount the domain routes
            logger.info('Domains mode : the list of domains is retrieves from the configuration file')
            for domain, m_domain in DOMAINS.items():
                if domain not in self.api_routes.keys():
                    raise Exception(f'The domain does not have a schema: {domain}')
                routes.append(
                    Route(f'/{domain}', JSONRoute(self.api_routes[domain]))
                )
                routes.append(
                    Mount(f'/{domain}', routes=gen_domain_routes(m_domain))
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
            }
        )

        self.__application.add_middleware(
            DomainMiddleware,
            config=CONFIG
        )

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
