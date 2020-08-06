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

    @pytest.mark.skip
    def test_domain_commands(self, project_runner):
        res = project_runner(['domain', 'foobar'])
        assert res.exit_code == 2
        res = project_runner(['domain', '--help'])
        assert res.exit_code == 0
        res = project_runner(['domain', 'create', '--help'])
        assert res.exit_code == 0
        res = project_runner(['domain', 'read', '--help'])
        assert res.exit_code == 0
        res = project_runner(['domain', 'update', '--help'])
        assert res.exit_code == 0
        res = project_runner(['domain', 'delete', '--help'])
        assert res.exit_code == 0

    @pytest.mark.skip
    def test_domain_create(self, project_runner):
        DOMNAME='tmp_domain'
        res = project_runner(['domain', 'create', DOMNAME])
        srcdir = os.path.join('domains', 'src',  DOMNAME)
        assert os.path.isdir(srcdir)
        moddir = os.path.join(srcdir, DOMNAME)
        assert os.path.isdir(moddir)
        setup = os.path.join(srcdir, 'setup.py')
        assert os.path.isfile(setup)
        initfile = os.path.join(moddir, '__init__.py')
        assert os.path.isfile(initfile)
        aclfile = os.path.join(moddir, 'acl.py')
        assert os.path.isfile(aclfile)
        aclsdir = os.path.join(moddir, 'acls')
        assert os.path.isdir(aclsdir)
        routersdir = os.path.join(moddir, 'routers')
        assert os.path.isdir(routersdir)

        try:
            dom_mod = importlib.import_module(DOMNAME, srcdir)
            assert hasattr(dom_mod, 'ROUTERS')
        except ImportError:
            assert False
