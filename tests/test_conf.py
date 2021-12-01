from unittest import TestCase
import sys
import pytest
from halfapi.halfapi import HalfAPI

class TestConf(TestCase):
    def setUp(self):
        self.args = { 
            'domain': {
                'name': 'dummy_domain',
                'router': 'dummy_domain.routers'
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
            SECRET,
            DOMAINSDICT,
            PROJECT_NAME,
            HOST,
            PORT,
            CONF_DIR
        )

        assert isinstance(CONFIG, dict)
        assert isinstance(SCHEMA, dict)
        assert isinstance(SECRET, str)
        assert isinstance(DOMAINSDICT(), dict)
        assert isinstance(PROJECT_NAME, str)
        assert isinstance(HOST, str)
        assert isinstance(PORT, str)
        assert str(int(PORT)) == PORT
        assert isinstance(CONF_DIR, str)
