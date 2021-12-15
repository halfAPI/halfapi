import importlib
import functools
import os
import sys
import json
from unittest import TestCase
from starlette.testclient import TestClient
from click.testing import CliRunner
from ..cli.cli import cli
from ..halfapi import HalfAPI
from ..half_domain import HalfDomain
from pprint import pprint

class TestDomain(TestCase):
    @property
    def router_module(self):
        return '.'.join((self.DOMAIN, self.ROUTERS))

    def setUp(self):
        # CLI
        class_ = CliRunner
        def invoke_wrapper(f):
            """Augment CliRunner.invoke to emit its output to stdout.

            This enables pytest to show the output in its logs on test
            failures.

            """
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                echo = kwargs.pop('echo', False)
                result = f(*args, **kwargs)

                if echo is True:
                    sys.stdout.write(result.output)

                return result

            return wrapper

        class_.invoke = invoke_wrapper(class_.invoke)
        self.runner = class_(mix_stderr=False)

        # HTTP
        self.halfapi_conf = {
            'domain': {}
        }

        self.halfapi_conf['domain'][self.DOMAIN] = {
            'name': self.DOMAIN,
            'router': self.ROUTERS,
            'prefix': False,
            'enabled': True,
            'config': {
                'test': True
            }
        }

        self.halfapi = HalfAPI(self.halfapi_conf)

        self.client = TestClient(self.halfapi.application)



    def tearDown(self):
        pass

    def check_domain(self):
        result = None
        try:
            result = self.runner.invoke(cli, '--version')
            self.assertEqual(result.exit_code, 0)
            result = self.runner.invoke(cli, ['domain', self.DOMAIN])
            self.assertEqual(result.exit_code, 0)
            result_d = json.loads(result.stdout)
            result = self.runner.invoke(cli, ['run', '--help'])
            self.assertEqual(result.exit_code, 0)
            result = self.runner.invoke(cli, ['run', '--dryrun', self.DOMAIN])
            self.assertEqual(result.exit_code, 0)
        except AssertionError as exc:
            print(f'Result {result}')
            print(f'Stdout {result.stdout}')
            print(f'Stderr {result.stderr}')
            raise exc


        return result_d

    def check_routes(self):
        r = self.client.get('/')
        assert r.status_code == 200
        schemas = r.json()
        assert isinstance(schemas, list)
        for schema in schemas:
            assert isinstance(schema, dict)
            assert 'openapi' in schema
            assert 'info' in schema
            assert 'paths' in schema
            assert 'domain' in schema

        r = self.client.get('/halfapi/acls')
        assert r.status_code == 200
        d_r = r.json()
        assert isinstance(d_r, dict)

        assert self.DOMAIN in d_r.keys()

        ACLS = HalfDomain.acls(self.DOMAIN)
        assert len(ACLS) == len(d_r[self.DOMAIN])

        for acl_name in ACLS:
            assert acl_name[0] in d_r[self.DOMAIN]
