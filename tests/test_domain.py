import pytest
from halfapi.testing.test_domain import TestDomain
from pprint import pprint
import logging
logger = logging.getLogger()

class TestDummyDomain(TestDomain):
    from .dummy_domain import domain
    __name__ = domain.get('name')
    __routers__ = domain.get('routers')

    DOMAIN = __name__
    CONFIG = {'test': True}

    def test_domain(self):
        self.check_domain()

    def test_routes(self):
        self.check_routes()

    def test_html_route(self):
        res = self.client.request('get', '/ret_type')
        assert res.status_code == 200
        assert isinstance(res.content.decode(), str)
        assert res.headers['content-type'].split(';')[0] == 'text/html'

        res = self.client.request('get', '/ret_type/h24')
        assert res.status_code == 200
        assert isinstance(res.content.decode(), str)
        assert res.headers['content-type'].split(';')[0] == 'text/html'

        res = self.client.request('get', '/ret_type/h24/config')
        assert res.status_code == 200
        assert isinstance(res.content.decode(), str)
        assert res.headers['content-type'].split(';')[0] == 'text/html'

        res = self.client.request('post', '/ret_type/h24/config', json={
            'trou': 'glet'
        })
        assert res.status_code == 200
        assert isinstance(res.content.decode(), str)
        assert res.headers['content-type'].split(';')[0] == 'text/html'

    def test_arguments__get_routes(self):
        res = self.client.request('post', '/arguments?foo=1&x=3')

        assert res.status_code == 400

        arg_dict = {'foo': '1', 'bar': '2', 'x': '3'}
        res = self.client.request('get', '/arguments?foo=1&bar=2&x=3')
        assert res.json() == arg_dict

        res = self.client.request('get', '/arguments?foo=1&bar=2&x=3&y=4')
        assert res.json() == arg_dict

    def test_arguments_post_routes(self):
        arg_dict = {}
        res = self.client.request('post', '/arguments', json=arg_dict)

        assert res.status_code == 400

        arg_dict = {'foo': '1', 'bar': '3'}
        res = self.client.request('post', '/arguments', json=arg_dict)

        assert res.status_code == 400

        arg_dict = {'foo': '1', 'baz': '3'}
        res = self.client.request('post', '/arguments', json=arg_dict)

        assert res.json() == arg_dict

        arg_dict = {'foo': '1', 'baz': '3', 'truebidoo': '4'}
        res = self.client.request('post', '/arguments', json=arg_dict)

        assert res.json() == arg_dict

        res = self.client.request('post', '/arguments', json={ **arg_dict, 'y': '4'})
        assert res.json() == arg_dict

        res = self.client.request('post', '/arguments', json={ **arg_dict, 'z': True})
        assert res.json() == {**arg_dict, 'z': True}

    def test_schema_path_params(self):
        res = self.client.request('get', '/halfapi/schema')
        schema = res.json()

        logger.debug(schema)

        assert len(schema['paths']) > 0
        route = schema['paths']['/path_params/{first}/one/{second}/two/{third}']

        assert 'parameters' in route['get']
        parameters = route['get']['parameters']

        assert len(parameters) == 3

        param_map = {
            elt['name']: elt
            for elt in parameters
        }

        assert param_map['second']['description'] == 'second parameter description test'




