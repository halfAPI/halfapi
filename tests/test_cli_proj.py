#!/usr/bin/env python3
import os
import subprocess
import importlib
import tempfile
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from configparser import ConfigParser

PROJNAME = os.environ.get('PROJ','tmp_api')


@pytest.mark.incremental
class TestCliProj():
    def test_cmds(self, project_runner):
        assert project_runner('--help').exit_code == 0
        #assert project_runner('run', '--help').exit_code == 0
        #assert project_runner('domain', '--help').exit_code == 0


    def test_domain_commands(self, project_runner):
        r = project_runner('domain')
        assert r.exit_code == 0

    @pytest.mark.skip
    def test_config_commands(self, project_runner):
        try:
            r = project_runner('config')
            assert r.exit_code == 0
        except AssertionError as exc:
            subprocess.call(['tree', '-a'])
            raise exc

