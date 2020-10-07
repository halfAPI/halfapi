"""
DomainMiddleware
"""

from starlette.middleware.base import (BaseHTTPMiddleware,
    RequestResponseEndpoint)
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Scope, Send, Receive

from .routes import api_routes
from .domain import d_domains

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


    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Scans routes and acls of each domain in config
        """
        self.domains = d_domains(self.config)

        for domain, m_domain in self.domains.items():
            self.api[domain], self.acl[domain] = api_routes(m_domain)

        scope_ = scope.copy()
        scope_['domains'] = self.domains
        scope_['api'] = self.api
        scope_['acl'] = self.acl
        request = Request(scope_, receive)
        response = await self.dispatch(request, self.call_next)
        await response(scope_, receive, send)


    async def dispatch(self, request: Request,
        call_next: RequestResponseEndpoint) -> Response:

        response = await call_next(request)
        return response
