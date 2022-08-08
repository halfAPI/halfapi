import pytest
from halfapi.testing.test_domain import TestDomain
from pprint import pprint

class TestDummyDomain(TestDomain):
    from .dummy_domain import __name__, __routers__

    DOMAIN = __name__
    CONFIG = {'test': True}

    def test_domain(self):
        self.check_domain()

    def test_routes(self):
        self.check_routes()

    def test_html_route(self):
        res = self.client.get('/ret_type')
        assert res.status_code == 200
        assert isinstance(res.content.decode(), str)
        assert res.headers['content-type'].split(';')[0] == 'text/html'
