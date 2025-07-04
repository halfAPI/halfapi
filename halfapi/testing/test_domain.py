import importlib
import functools
import os
import sys
import json
from json.decoder import JSONDecodeError
import toml
from unittest import TestCase
from starlette.testclient import TestClient
from click.testing import CliRunner
from ..cli.cli import cli
from ..halfapi import HalfAPI
from ..half_domain import HalfDomain
from ..conf import DEFAULT_CONF
from pprint import pprint
import tempfile

class TestDomain(TestCase):
    @property
    def domain_name(self):
        return getattr(self, 'DOMAIN')

    @property
    def module_name(self):
        return getattr(self, 'MODULE', self.domain_name)

    @property
    def acl_path(self):
        return getattr(self, 'ACL', '.acl')

    @property
    def router_path(self):
        return getattr(self, 'ROUTERS', '.routers')

    @property
    def router_module(self):
        return '.'.join((self.module_name, self.ROUTERS))


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
        self.runner = class_()

        # HTTP
        # Fake default values of default configuration
        self.halfapi_conf = {
            'secret': 'testsecret',
            'production': False,
            'domain': {}
        }

        self.halfapi_conf['domain'][self.domain_name] = {
            'name': self.domain_name,
            'router': self.router_path,
            'acl': self.acl_path,
            'module': self.module_name,
            'prefix': False,
            'enabled': True,
            'config': getattr(self, 'CONFIG', {})
        }

        _, self.config_file = tempfile.mkstemp()
        with open(self.config_file, 'w') as fh:
            fh.write(toml.dumps(self.halfapi_conf))

        self.halfapi = HalfAPI(self.halfapi_conf)

        self.client = TestClient(self.halfapi.application)

        self.module = importlib.import_module(
            self.module_name
        )


    def tearDown(self):
        pass

    def check_domain(self):
        result = None
        try:
            result = self.runner.invoke(cli, '--version')
            self.assertEqual(result.exit_code, 0)
            result = self.runner.invoke(cli, ['domain', '--read', self.DOMAIN, self.config_file])
            self.assertEqual(result.exit_code, 0)
            result_d = json.loads(result.stdout)
            result = self.runner.invoke(cli, ['run', '--help'])
            self.assertEqual(result.exit_code, 0)
            # result = self.runner.invoke(cli, ['run', '--dryrun', self.DOMAIN])
            # self.assertEqual(result.exit_code, 0)
        except AssertionError as exc:
            print(f'Result {result}')
            print(f'Stdout {result.stdout}')
            print(f'Stderr {result.stderr}')
            raise exc
        except JSONDecodeError as exc:
            print(f'Result {result}')
            print(f'Stdout {result.stdout}')
            raise exc



        return result_d

    def check_routes(self):
        r = self.client.request('get', '/')
        assert r.status_code == 200
        schema = r.json()
        assert isinstance(schema, dict)
        assert 'openapi' in schema
        assert 'info' in schema
        assert 'paths' in schema

        r = self.client.request('get', '/halfapi/acls')
        assert r.status_code == 200
        d_r = r.json()
        assert isinstance(d_r, dict)
        assert self.domain_name in d_r.keys()

        ACLS = HalfDomain.acls(self.module, self.acl_path)
        assert len(ACLS) == len(d_r[self.domain_name])

        for acl_rule in ACLS:
            assert len(acl_rule.name) > 0
            assert acl_rule.name in d_r[self.domain_name]
            assert len(acl_rule.documentation) > 0
            assert isinstance(acl_rule.priority, int)
            assert acl_rule.priority >= 0

            if acl_rule.public is True:
                r = self.client.request('get', f'/halfapi/acls/{acl_rule.name}')
                assert r.status_code in [200, 401]
