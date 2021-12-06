from unittest import TestCase
import sys
import pytest
from halfapi.halfapi import HalfAPI

class TestConf(TestCase):
    def setUp(self):
        self.args = {
            'domain': {
                'dummy_domain': {
                    'name': 'dummy_domain',
                    'router': '.routers',
                    'enabled': True,
                    'prefix': False,
                }
            }
        }
    def tearDown(self):
        pass

    def test_conf_production_default(self):
        halfapi = HalfAPI({
            **self.args
        })
        assert halfapi.PRODUCTION is True

    def test_conf_production_true(self):
        halfapi = HalfAPI({
            **self.args,
            'production': True,
        })
        assert halfapi.PRODUCTION is True

    def test_conf_production_false(self):
        halfapi = HalfAPI({
            **self.args,
            'production': False,
        })
        assert halfapi.PRODUCTION is False

    def test_conf_variables(self):
        from halfapi.conf import (
            CONFIG,
            SCHEMA,
        )

        assert isinstance(CONFIG, dict)
        assert isinstance(CONFIG.get('project_name'), str)
        assert isinstance(SCHEMA, dict)
        assert isinstance(CONFIG.get('secret'), str)
        assert isinstance(CONFIG.get('host'), str)
        assert isinstance(CONFIG.get('port'), int)
