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

        res = self.client.get('/ret_type/h24')
        assert res.status_code == 200
        assert isinstance(res.content.decode(), str)
        assert res.headers['content-type'].split(';')[0] == 'text/html'

        res = self.client.get('/ret_type/h24/config')
        assert res.status_code == 200
        assert isinstance(res.content.decode(), str)
        assert res.headers['content-type'].split(';')[0] == 'text/html'

        res = self.client.post('/ret_type/h24/config', {
            'trou': 'glet'
        })
        assert res.status_code == 200
        assert isinstance(res.content.decode(), str)
        assert res.headers['content-type'].split(';')[0] == 'text/html'

    def test_arguments__get_routes(self):
        res = self.client.post('/arguments?foo=1&x=3')

        assert res.status_code == 400

        arg_dict = {'foo': '1', 'bar': '2', 'x': '3'}
        res = self.client.get('/arguments?foo=1&bar=2&x=3')
        assert res.json() == arg_dict

        res = self.client.get('/arguments?foo=1&bar=2&x=3&y=4')
        assert res.json() == arg_dict

    def test_arguments_post_routes(self):
        arg_dict = {}
        res = self.client.post('/arguments', arg_dict)

        assert res.status_code == 400

        arg_dict = {'foo': '1', 'bar': '3'}
        res = self.client.post('/arguments', arg_dict)

        assert res.status_code == 400

        arg_dict = {'foo': '1', 'baz': '3'}
        res = self.client.post('/arguments', arg_dict)

        assert res.json() == arg_dict

        arg_dict = {'foo': '1', 'baz': '3', 'truebidoo': '4'}
        res = self.client.post('/arguments', arg_dict)

        assert res.json() == arg_dict

        res = self.client.post('/arguments', { **arg_dict, 'y': '4'})
        assert res.json() == arg_dict
