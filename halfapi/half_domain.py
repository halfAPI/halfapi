import importlib

from starlette.applications import Starlette
from starlette.routing import Router

from .half_route import HalfRoute
from .lib.routes import gen_domain_routes, gen_schema_routes
from .lib.domain_middleware import DomainMiddleware
from .logging import logger

class HalfDomain(Starlette):
    def __init__(self, app, domain, router=None, config={}):
        self.app = app

        self.m_domain = importlib.import_module(domain)
        self.name = getattr('__name__', domain, domain)

        if not router:
            self.router = getattr('__router__', domain, '.routers')
        else:
            self.router = router

        self.m_router = importlib.import_module(self.router, domain)

        self.m_acl = importlib.import_module(f'{domain}.acl')

        self.config = config

        """
        if domain:
            m_domain = importlib.import_module(domain)
            if not router:
                router = getattr('__router__', domain, '.routers')
            m_domain_router = importlib.import_module(router, domain)
            m_domain_acl = importlib.import_module(f'{domain}.acl')

        if not(m_domain and m_domain_router and m_domain_acl):
            raise Exception('Cannot import domain')

        self.schema = domain_schema(m_domain)

        routes = [ Route('/', JSONRoute(self.schema)) ]
        """

        logger.info('HalfDomain creation %s %s', domain, config)
        super().__init__(
            routes=gen_domain_routes(self.m_router),
            middleware=[
                (DomainMiddleware,
                    {
                    'domain': self.name,
                    'config': self.config
                    }
                )
            ]
        )

    @staticmethod
    def acls(domain):
        """ Returns the ACLS constant for the given domain
        """
        m_acl = importlib.import_module(f'{domain}.acl')
        try:
            return getattr(m_acl, 'ACLS')
        except AttributeError:
            raise Exception(f'Missing acl.ACLS constant in {domain} module')
