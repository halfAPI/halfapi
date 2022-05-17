from halfapi.testing.test_domain import TestDomain
from pprint import pprint

class TestDummyDomain(TestDomain):
    from .dummy_domain import __name__, __routers__

    DOMAIN = __name__
    ROUTERS = __routers__
    ACL = '.acl'

    def test_domain(self):
        self.check_domain()

    def test_routes(self):
        self.check_routes()
