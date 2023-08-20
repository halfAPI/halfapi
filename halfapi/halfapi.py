#!/usr/bin/env python3
"""
app.py is the file that is read when launching the application using an asgi
runner.

It defines the following globals :

    - routes (contains the Route objects for the application)
    - application (the asgi application itself - a starlette object)

"""
import sys
import logging
import time
import importlib
from datetime import datetime

# asgi framework
from starlette.applications import Starlette
from starlette.authentication import UnauthenticatedUser
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.routing import Router, Route, Mount
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse
from starlette.middleware.authentication import AuthenticationMiddleware

from timing_asgi import TimingMiddleware
from timing_asgi.integrations import StarletteScopeToName

# module libraries

from .lib.constants import API_SCHEMA_DICT
from .lib.domain_middleware import DomainMiddleware
from .lib.timing import HTimingClient
from .lib.jwt_middleware import JWTAuthenticationBackend, on_auth_error
from .lib.responses import (ORJSONResponse, UnauthorizedResponse,
    NotFoundResponse, InternalServerErrorResponse, NotImplementedResponse,
    ServiceUnavailableResponse, gen_exception_route)
from .lib.domain import NoDomainsException
from .lib.routes import gen_schema_routes, JSONRoute
from .lib.schemas import schema_json
from .logging import logger, config_logging
from .half_domain import HalfDomain
from halfapi import __version__

class HalfAPI(Starlette):
    def __init__(self,
        config,
        d_routes=None):
        # Set log level (defaults to debug)
        config_logging(
            getattr(logging, config.get('loglevel', 'DEBUG').upper(), 'DEBUG')
        )
        self.config = config
        SECRET = self.config.get('secret')
        PRODUCTION = self.config.get('production', True)
        DRYRUN = self.config.get('dryrun', False)
        TIMINGMIDDLEWARE = self.config.get('timingmiddleware', False)

        if DRYRUN:
            logger.info('HalfAPI starting in dry-run mode')
        else:
            logger.info('HalfAPI starting')


        self.PRODUCTION = PRODUCTION
        self.SECRET = SECRET

        # Domains

        """ HalfAPI routes (if not PRODUCTION, includes debug routes)
        """
        routes = []
        routes.append(
            Mount('/halfapi', routes=list(self.halfapi_routes()))
        )

        logger.debug('Config: %s', self.config)

        domains = {
            key: elt
            for key, elt in self.config.get('domain', {}).items()
            if elt.get('enabled', False)
        }

        logger.debug('Active domains: %s', domains)

        if d_routes:
            # Mount the routes from the d_routes argument - domain-less mode
            logger.info('Domain-less mode : the given schema defines the activated routes')
            for route in gen_schema_routes(d_routes):
                routes.append(route)
        else:
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
                401: gen_exception_route(UnauthorizedResponse),
                404: gen_exception_route(NotFoundResponse),
                500: gen_exception_route(HalfAPI.exception),
                501: gen_exception_route(NotImplementedResponse),
                503: gen_exception_route(ServiceUnavailableResponse)
            },
            on_startup=startup_fcts
        )

        schemas = []

        self.__domains = {}

        for key, domain in domains.items():
            if not isinstance(domain, dict):
                continue

            dom_name = domain.get('name', key)
            if not domain.get('enabled', False):
                continue

            if not domain.get('prefix', False):
                if len(domains.keys()) > 1:
                    raise Exception('Cannot use multiple domains and set prefix to false')
                path = '/'
            else:
                path = f'/{dom_name}'

            logger.debug('Mounting domain %s on %s', domain.get('name'), path)

            domain_key = domain.get('name', key)

            add_domain_args = {
                **domain,
                'path': path
            }

            self.add_domain(**add_domain_args)

            schemas.append(self.__domains[domain_key].schema())


        self.add_route('/', JSONRoute(schemas))

        if SECRET:
            self.add_middleware(
                AuthenticationMiddleware,
                backend=JWTAuthenticationBackend(),
                on_error=on_auth_error
            )

        if not PRODUCTION and TIMINGMIDDLEWARE:
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
        """
        description: Version route
        responses:
          200:
            description: Currently running HalfAPI's version
        """
        return Response(self.version)

    @staticmethod
    async def exception(request: Request, exc: HTTPException):
        logger.critical(exc, exc_info=True)
        return InternalServerErrorResponse()

    @property
    def application(self):
        return self

    def halfapi_routes(self):
        """ Halfapi default routes
        """

        async def get_user(request, *args, **kwargs):
            """
            description: WhoAmI route
            responses:
              200:
                description: The currently logged-in user
                content:
                  application/json:
                    schema:
                      type: object
            """
            return ORJSONResponse({'user':request.user})

        yield Route('/whoami', get_user)
        yield Route('/schema', schema_json)
        yield Mount('/acls', self.acls_router())
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

    def acls_router(self):
        mounts = {}

        for domain, domain_conf in self.config.get('domain', {}).items():
            if isinstance(domain_conf, dict) and domain_conf.get('enabled', False):
                mounts['domain'] = HalfDomain.acls_router(
                    domain,
                    module_path=domain_conf.get('module'),
                    acl=domain_conf.get('acl')
                )

        if len(mounts) > 1:
            return Router([
                Mount(f'/{domain}', acls_router)
                for domain, acls_router in mounts.items()
            ])
        elif len(mounts) == 1:
            return Mount('/', mounts.popitem()[1])
        else:
            return Router()

    @property
    def domains(self):
        return self.__domains

    def add_domain(self, **kwargs):

        if not kwargs.get('enabled'):
            raise Exception(f'Domain not enabled ({kwargs})')

        name = kwargs['name']

        self.config['domain'][name] = kwargs.get('config', {})

        if not kwargs.get('module'):
            module = name
        else:
            module = kwargs.get('module')

        try:
            self.__domains[name] = HalfDomain(
                name,
                module=importlib.import_module(module),
                router=kwargs.get('router'),
                acl=kwargs.get('acl'),
                app=self
            )

        except ImportError as exc:
            print(
                'Cannot instantiate HalfDomain {} with module {}'.format(
                name,
                module
            ))
            raise exc

        self.mount(kwargs.get('path', name), self.__domains[name])

        return self.__domains[name]


def __main__():
    return HalfAPI(CONFIG).application

if __name__ == '__main__':
    __main__()


