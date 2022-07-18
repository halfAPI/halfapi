"""
DomainMiddleware
"""
from starlette.datastructures import URL
from starlette.middleware.base import (BaseHTTPMiddleware,
    RequestResponseEndpoint)
from starlette.requests import Request
from starlette.responses import Response

from ..logging import logger

class DomainMiddleware(BaseHTTPMiddleware):
    """
    DomainMiddleware adds the api routes and acls to the following scope keys :

        - api
        - acl
    """

    def __init__(self, app, domain):
        """ app: HalfAPI instance
        """
        logger.info('DomainMiddleware app:%s domain:%s', app, domain)
        super().__init__(app)
        self.domain = domain
        self.request = None


    async def dispatch(self, request: Request,
        call_next: RequestResponseEndpoint) -> Response:
        """
        Call of the route fonction (decorated or not)
        """

        request.scope['domain'] = self.domain['name']
        if hasattr(request.app, 'config') \
          and isinstance(request.app.config, dict):
            # Set the config scope to the domain's config
            request.scope['config'] = request.app.config.get(
                'domain', {}
            ).get(
                self.domain['name'], {}
            ).copy()

            # TODO: Remove in 0.7.0
            config = request.scope['config'].copy()
            request.scope['config']['domain'] = {}
            request.scope['config']['domain'][self.domain['name']] = {}
            request.scope['config']['domain'][self.domain['name']]['config'] = config
            


        else:
            logger.debug('%s', request.app)
            logger.debug('%s', getattr(request.app, 'config', None))

        response = await call_next(request)

        if 'acl_pass' in request.scope:
            # Set the http header "x-acl" if an acl was used on the route
            response.headers['x-acl'] = request.scope['acl_pass']

        if 'args' in request.scope:
            # Set the http headers "x-args-required" and "x-args-optional"

            if len(request.scope['args'].get('required', set())):
                response.headers['x-args-required'] = \
                    ','.join(request.scope['args']['required'])
            if len(request.scope['args'].get('optional', set())):
                response.headers['x-args-optional'] = \
                    ','.join(request.scope['args']['optional'])

        if len(request.scope.get('out', set())):
            response.headers['x-out'] = \
                ','.join(request.scope['out'])


        response.headers['x-domain'] = self.domain['name']

        return response
