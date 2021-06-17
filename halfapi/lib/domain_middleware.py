"""
DomainMiddleware
"""
import configparser
import logging

from starlette.datastructures import URL
from starlette.middleware.base import (BaseHTTPMiddleware,
    RequestResponseEndpoint)
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Scope, Send, Receive

from .routes import api_routes
from .domain import d_domains

logger = logging.getLogger('uvicorn.asgi')

class DomainMiddleware(BaseHTTPMiddleware):
    """
    DomainMiddleware adds the api routes and acls to the following scope keys :

        - domains
        - api
        - acl
    """

    def __init__(self, app, config):
        super().__init__(app)
        self.config = config
        self.domains = {}
        self.api = {}
        self.acl = {}
        self.request = None


    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Scans routes and acls of the domain in the first part of the path
        """
        domain = scope['path'].split('/')[1]

        self.domains = self.config.get('domains', {})

        if len(domain) == 0 or domain == 'halfapi':
            for domain in self.domains:
                self.api[domain], self.acl[domain] = api_routes(self.domains[domain])
        elif domain in self.domains:
            self.api[domain], self.acl[domain] = api_routes(self.domains[domain])
        else:
            logger.error('domain not in self.domains %s / %s',
                    scope['path'],
                    self.domains)

        scope_ = scope.copy()
        scope_['domains'] = self.domains
        scope_['api'] = self.api
        scope_['acl'] = self.acl

        cur_path = URL(scope=scope).path
        if cur_path[0] == '/':
            current_domain = cur_path[1:].split('/')[0]
        else:
            current_domain = cur_path.split('/')[0]

        try:
            scope_['config'] = self.config.copy()
        except configparser.NoSectionError:
            logger.debug(
                'No specific configuration for domain **%s**', current_domain)
            scope_['config'] = {}


        self.request = Request(scope_, receive)
        response = await self.dispatch(self.request, self.call_next)
        await response(scope_, receive, send)


    async def dispatch(self, request: Request,
        call_next: RequestResponseEndpoint) -> Response:
        """
        Call of the route fonction (decorated or not)
        """

        response = await call_next(request)

        if 'acl_pass' in self.request.scope:
            # Set the http header "x-acl" if an acl was used on the route
            response.headers['x-acl'] = self.request.scope['acl_pass']

        if 'args' in self.request.scope:
            # Set the http headers "x-args-required" and "x-args-optional"

            if 'required' in self.request.scope['args']:
                response.headers['x-args-required'] = \
                    ','.join(self.request.scope['args']['required'])
            if 'optional' in self.request.scope['args']:
                response.headers['x-args-optional'] = \
                    ','.join(self.request.scope['args']['optional'])
        return response
