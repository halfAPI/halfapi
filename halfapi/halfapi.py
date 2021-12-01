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

        domain = config.get('domain')['name']
        router = config.get('domain').get('router', None)

        if not (domain and router):
            raise NoDomainsException()

        self.PRODUCTION = PRODUCTION
        self.CONFIG = CONFIG
        self.SECRET = SECRET

        self.__application = None

        m_domain = m_domain_router = m_domain_acl = None
        if domain:
            m_domain = importlib.import_module(f'{domain}')
            if not router:
                router = getattr('__router__', domain, '.routers')
            m_domain_router = importlib.import_module(router)
            m_domain_acl = importlib.import_module(f'{domain}.acl')

        if not(m_domain and m_domain_router and m_domain_acl):
            raise Exception('Cannot import domain')

        self.schema = domain_schema(m_domain)

        routes = [ Route('/', JSONRoute(self.schema)) ]

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
        else:
            for route in gen_domain_routes(m_domain_router):
                routes.append(route)

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
            domain=domain,
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

    @staticmethod
    def api_schema(domain):
        pass
