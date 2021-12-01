from halfapi.testing.test_domain import TestDomain
from dummy_domain import __name__, __routers__
from pprint import pprint

class TestDummyDomain(TestDomain):
    DOMAIN = __name__
    ROUTERS = __routers__

    def test_domain(self):
        self.check_domain()
