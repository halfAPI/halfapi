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
        self.request = None


    async def dispatch(self, request: Request,
        call_next: RequestResponseEndpoint) -> Response:
        """
        Call of the route fonction (decorated or not)
        """

        response = await call_next(request)

        if 'acl_pass' in request.scope:
            # Set the http header "x-acl" if an acl was used on the route
            response.headers['x-acl'] = request.scope['acl_pass']

        if 'args' in request.scope:
            # Set the http headers "x-args-required" and "x-args-optional"

            if 'required' in request.scope['args']:
                response.headers['x-args-required'] = \
                    ','.join(request.scope['args']['required'])
            if 'optional' in request.scope['args']:
                response.headers['x-args-optional'] = \
                    ','.join(request.scope['args']['optional'])


        return response
