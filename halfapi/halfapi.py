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
from .lib.domain import NoDomainsException
from .lib.routes import gen_schema_routes, JSONRoute
from .lib.schemas import schema_json, get_acls
from .logging import logger, config_logging
from .half_domain import HalfDomain
from halfapi import __version__

class HalfAPI(Starlette):
    def __init__(self, config,
        d_routes=None):
        config_logging(logging.DEBUG)
        self.config = config

        SECRET = self.config.get('secret')
        PRODUCTION = self.config.get('production', True)
        DRYRUN = self.config.get('dryrun', False)

        self.PRODUCTION = PRODUCTION
        self.SECRET = SECRET

        # Domains

        """ HalfAPI routes (if not PRODUCTION, includes debug routes)
        """
        routes = []
        routes.append(
            Mount('/halfapi', routes=list(self.halfapi_routes()))
        )

        logger.info('Config: %s', self.config)
        logger.info('Active domains: %s',
            list(filter(
                lambda n: n.get('enabled', False),
                self.config.get('domain', {}).values())))

        if d_routes:
            # Mount the routes from the d_routes argument - domain-less mode
            logger.info('Domain-less mode : the given schema defines the activated routes')
            for route in gen_schema_routes(d_routes):
                routes.append(route)
        else:
            logger.info('NO ROUTES')
            pass

        startup_fcts = []

        if DRYRUN:
            startup_fcts.append(
                HalfAPI.wait_quit()
            )

        super().__init__(
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

        schemas = []

        self.__domains = {}

        for key, domain in self.config.get('domain', {}).items():
            if not isinstance(domain, dict):
                continue

            dom_name = domain.get('name', key)
            if not domain.get('enabled', False):
                continue

            if not domain.get('prefix', False):
                if len(self.config.get('domain').keys()) > 1:
                    raise Exception('Cannot use multiple domains and set prefix to false')
                path = '/'
            else:
                path = f'/{dom_name}'

            logger.debug('Mounting domain %s on %s', domain.get('name'), path)

            domain_key = domain.get('name', key)

            self.add_domain(domain_key, domain.get('router'), path)

            schemas.append(self.__domains[domain_key].schema())


        self.add_route('/', JSONRoute(schemas))

        self.add_middleware(
            AuthenticationMiddleware,
            backend=JWTAuthenticationBackend()
        )

        if not PRODUCTION:
            self.add_middleware(
                TimingMiddleware,
                client=HTimingClient(),
                metric_namer=StarletteScopeToName(prefix="halfapi",
                starlette_app=self)
            )



    @property
    def version(self):
        return __version__

    async def version_async(self, request, *args, **kwargs):
        return Response(self.version)

    @property
    def application(self):
        return self

    def halfapi_routes(self):
        """ Halfapi default routes
        """

        async def get_user(request, *args, **kwargs):
            return ORJSONResponse({'user':request.user})

        yield Route('/whoami', get_user)
        yield Route('/schema', schema_json)
        yield Route('/acls', self.acls_route())
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

    def acls_route(self):
        res = {
            domain: HalfDomain.acls_route(domain)
            for domain, domain_conf in self.config.get('domain', {}).items()
            if isinstance(domain_conf, dict) and domain_conf.get('enabled', False)
        }

        async def wrapped(req, *args, **kwargs):
            for domain, domain_acls in res.items():
                for acl_name, d_acl in domain_acls.items():
                    fct = d_acl['callable']
                    if not callable(fct):
                        raise Exception(
                            'No callable function in acl definition %s',
                            acl_name)

                    fct_result = fct(req, *args, **kwargs)
                    if callable(fct_result):
                        fct_result = fct()(req, *args, **kwargs)

                    d_acl['result'] = fct_result

            return ORJSONResponse(res)

        return wrapped

    @property
    def domains(self):
        return self.__domains

    def add_domain(self, name, router=None, path='/', config=None):
        if config:
            self.config['domain'][name] = config

        self.__domains[name] = HalfDomain(
            name,
            router,
            self
        )

        self.mount(path, self.__domains[name])

        return self.__domains[name]
