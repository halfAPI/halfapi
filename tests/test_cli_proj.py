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
        print(os.getcwd())
        assert project_runner('--help').exit_code == 0
        #assert project_runner('run', '--help').exit_code == 0
        #assert project_runner('domain', '--help').exit_code == 0


    def test_config_commands(self, project_runner):
        assert project_runner('config') == 0


    def test_domain_commands(self, subproc):
        assert project_runner('domain') == 0
