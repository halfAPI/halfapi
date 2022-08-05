#!/usr/bin/env python3
import os
import subprocess
import importlib
import tempfile
from unittest.mock import patch
import json

import pytest
from click.testing import CliRunner
from configparser import ConfigParser

PROJNAME = os.environ.get('PROJ','tmp_api')


class TestCliProj():
    def test_cmds(self, project_runner):
        assert project_runner('--help').exit_code == 0
        #assert project_runner('run', '--help').exit_code == 0
        #assert project_runner('domain', '--help').exit_code == 0


    def test_domain_commands(self, project_runner):
        """ TODO: Test create command
        """
        r = project_runner('domain')
        print(r.stdout)
        assert r.exit_code == 1
        _, tmp_conf = tempfile.mkstemp()
        with open(tmp_conf, 'w') as fh:
            fh.write(
                json.dumps({
                    'domain': {
                        'dummy_domain': {
                            'name': 'dummy_domain',
                            'enabled': True
                        }
                    }
                })
            )

        r = project_runner(f'domain dummy_domain {tmp_conf}')
        print(r.stdout)
        assert r.exit_code == 0


    def test_config_commands(self, project_runner):
        try:
            r = project_runner('config')
            assert r.exit_code == 0
        except AssertionError as exc:
            subprocess.call(['tree', '-a'])
            raise exc

