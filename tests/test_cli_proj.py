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

@pytest.fixture
def subproc(project_runner):
    def caller(cmd):
        proc = subprocess.Popen(cmd.split(' '))
        return proc.wait()
    return caller

@pytest.mark.incremental
class TestCliProj():
    def test_cmds(self, subproc):
        assert subproc('halfapi run --help') == 0
        assert subproc('halfapi domain --help') == 0

    def test_config_commands(self, subproc):
        res = subproc('halfapi config pr00t')
        assert res == 2
        res = subproc('halfapi config --help')
        assert res == 0
        res = subproc('halfapi config')
        assert res == 0

    def test_domain_commands(self, subproc):
        res = subproc('halfapi domain foobar')
        assert res == 2
        res = subproc('halfapi domain --help')
        assert res == 0

    def test_domain_create(self, subproc):
        DOMNAME='tmp_domain'
        res = subproc(f'halfapi domain --create')
        assert res == 0
