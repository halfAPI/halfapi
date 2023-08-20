#!/usr/bin/env python3
import os
import subprocess
import importlib
import tempfile
from unittest.mock import patch
import json
import toml

import pytest
from click.testing import CliRunner
from configparser import ConfigParser
from halfapi.conf import DEFAULT_CONF, PROJECT_LEVEL_KEYS, DOMAIN_LEVEL_KEYS

PROJNAME = os.environ.get('PROJ','tmp_api')


class TestCliProj():
    def test_cmds(self, project_runner):
        assert project_runner('--help').exit_code == 0
        #assert project_runner('run', '--help').exit_code == 0
        #assert project_runner('domain', '--help').exit_code == 0


    def test_domain_commands(self, project_runner):
        """ TODO: Test create command
        """
        test_conf = {
            'project': {
                'port': '3010',
                'loglevel': 'warning'
            },
            'domain': {
                'dummy_domain': {
                    'port': 4242,
                    'name': 'dummy_domain',
                    'enabled': True
                }
            }
        }

        r = project_runner('domain')
        print(r.stdout)
        assert r.exit_code == 1
        _, tmp_conf = tempfile.mkstemp()
        with open(tmp_conf, 'w') as fh:
            fh.write(
                toml.dumps(test_conf)
            )

        r = project_runner(f'domain dummy_domain --conftest {tmp_conf}')
        assert r.exit_code == 0
        r_conf = toml.loads(r.stdout)
        for key, value in r_conf.items():
            if key == 'domain':
                continue
            assert key in PROJECT_LEVEL_KEYS
            if key == 'port':
                assert value == test_conf['domain']['dummy_domain']['port']
            elif key == 'loglevel':
                assert value == test_conf['project']['loglevel']
            else:
                assert value == DEFAULT_CONF[key.upper()]


        assert json.dumps(test_conf['domain']) == json.dumps(r_conf['domain'])

        for key in test_conf['domain']['dummy_domain'].keys():
            assert key in DOMAIN_LEVEL_KEYS

        # Default command "run"
        r = project_runner(f'domain dummy_domain --dry-run {tmp_conf}')
        print(r.stdout)
        assert r.exit_code == 0


    def test_config_commands(self, project_runner):
        try:
            r = project_runner('config')
            assert r.exit_code == 0
        except AssertionError as exc:
            subprocess.call(['tree', '-a'])
            raise exc

