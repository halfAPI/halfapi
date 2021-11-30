import importlib
import functools
import os
import sys
import json
from unittest import TestCase
from click.testing import CliRunner
from halfapi.cli.cli import cli
from pprint import pprint

class TestDomain(TestCase):
    DOMAIN = 'dummy_domain'
    ROUTERS = 'routers'

    @property
    def router_module(self):
        return '.'.join((self.DOMAIN, self.ROUTERS))

    def setUp(self):
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


    def tearDown(self):
        pass

    def test_routes(self):
        result = self.runner.invoke(cli, '--version')
        self.assertEqual(result.exit_code, 0)
        result = self.runner.invoke(cli, ['routes', '--export', self.router_module])
        self.assertEqual(result.exit_code, 0)
        print(result.stdout)
        # result_d = json.loads(result.stdout)
        # self.assertTrue()
