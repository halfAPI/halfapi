"""
DomainMiddleware
"""
import logging

from starlette.datastructures import URL
from starlette.middleware.base import (BaseHTTPMiddleware,
    RequestResponseEndpoint)
from starlette.requests import Request
from starlette.responses import Response

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

        l_path = URL(scope=request.scope).path.split('/')
        cur_domain = l_path[0]
        if len(cur_domain) == 0 and len(l_path) > 1:
            cur_domain = l_path[1]

        request.scope['domain'] = cur_domain
        request.scope['config'] = self.config['domain_config'][cur_domain] \
            if cur_domain in self.config.get('domain_config', {}) else {}

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

        response.headers['x-domain'] = cur_domain

        return response
