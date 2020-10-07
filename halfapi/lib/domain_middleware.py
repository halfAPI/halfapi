from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import Scope, Send, Receive

from .routes import api_routes
from .domain import d_domains

class DomainMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, config):
        super().__init__(app)
        self.config = config
        self.domains = d_domains(config)
        self.api = {}
        self.acl = {}

        for domain, m_domain in self.domains.items():
            self.api[domain], self.acl[domain] = api_routes(m_domain)


    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        scope_ = scope.copy()
        scope_['domains'] = self.domains
        scope_['api'] = self.api
        scope_['acl'] = self.acl

        request = Request(scope_, receive)
        response = await self.call_next(request)
        await response(scope_, receive, send)
        return response
