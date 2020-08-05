#!/usr/bin/env python3
import os
import subprocess
import importlib

import pytest
from click.testing import CliRunner
from configparser import ConfigParser

from halfapi import __version__
from halfapi.cli import cli
Cli = cli.cli

PROJNAME = os.environ.get('PROJ','tmp_api')

@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def dropdb():
    p = subprocess.Popen(['dropdb', f'halfapi_{PROJNAME}'])
    p.wait()
    yield 

    p = subprocess.Popen(['dropdb', f'halfapi_{PROJNAME}'])
    p.wait()

@pytest.fixture
def createdb():
    p = subprocess.Popen(['createdb', f'halfapi_{PROJNAME}'])
    p.wait()
    return


@pytest.mark.incremental
class TestCli():
    def test_options(self, runner, dropdb, createdb):
        # Wrong command
        with runner.isolated_filesystem():
            r = runner.invoke(Cli, ['foobar'])
            assert r.exit_code == 2

        # Test existing commands
        with runner.isolated_filesystem():
            r = runner.invoke(Cli, ['--help'])
            assert r.exit_code == 0

        with runner.isolated_filesystem():
            r = runner.invoke(Cli, ['--version'])
            assert r.exit_code == 0

        with runner.isolated_filesystem():
            r = runner.invoke(Cli, ['init', '--help'])
            assert r.exit_code == 0


    def test_init_project_fail(self, runner, dropdb):
        # Missing argument (project)
        testproject = 'testproject'
        r = runner.invoke(Cli, ['init'])
        assert r.exit_code == 2

        with runner.isolated_filesystem():
            # Fail : Wrong project name
            r = runner.invoke(Cli, ['init', 'test*-project'])
            assert r.exit_code == 1

        with runner.isolated_filesystem():
            # Fail : Already existing folder
            os.mkdir(testproject)
            r = runner.invoke(Cli, ['init', testproject])
            assert r.exit_code == 1

        with runner.isolated_filesystem():
            # Fail : Already existing nod
            os.mknod(testproject)
            r = runner.invoke(Cli, ['init', testproject])
            assert r.exit_code == 1

    def test_init_project(self, runner, dropdb, createdb):
        cp = ConfigParser()
        with runner.isolated_filesystem():
            env = {
                'HALFORM_CONF_DIR': os.environ.get('HALFORM_CONF_DIR', os.getcwd()),
                'HALFAPI_CONF_DIR': os.environ.get('HALFAPI_CONF_DIR', os.getcwd()),
            }

            res = runner.invoke(Cli, ['init', PROJNAME], env=env)
            try:
                assert os.path.isdir(PROJNAME)
                assert os.path.isdir(os.path.join(PROJNAME, '.halfapi'))


                # .halfapi/config check
                assert os.path.isfile(os.path.join(PROJNAME, '.halfapi', 'config'))
                cp.read(os.path.join(PROJNAME, '.halfapi', 'config'))
                assert cp.has_section('project')
                assert cp.has_option('project', 'name')
                assert cp.get('project', 'name') == PROJNAME
                assert cp.get('project', 'halfapi_version') == __version__

                # .halfapi/domains check
                assert os.path.isfile(os.path.join(PROJNAME, '.halfapi', 'domains'))
                cp.read(os.path.join(PROJNAME, '.halfapi', 'domains'))
                assert cp.has_section('domains')
            except AssertionError:
                subprocess.run(['tree', '-a', os.getcwd()])

            assert res.exit_code == 0
            assert res.exception is None

    def test_run_commands(self, runner, dropdb, createdb):
        def reloadcli():
            importlib.reload(cli)
            return cli.cli

        with runner.isolated_filesystem():
            res = runner.invoke(Cli, ['init', PROJNAME])
            assert res.exit_code == 0
            os.chdir(PROJNAME)
            Cli2 = reloadcli()
            res = runner.invoke(Cli2, ['run', '--help'])
            assert res.exception is None
            assert res.exit_code == 0

        with runner.isolated_filesystem():
            res = runner.invoke(Cli, ['init', PROJNAME])
            os.chdir(PROJNAME)
            res = runner.invoke(Cli, ['run', 'foobar'])
            assert res.exit_code == 2


    def test_domain_commands(self, runner, dropdb, createdb):
        with runner.isolated_filesystem():
            res = runner.invoke(Cli, ['init', PROJNAME])
            os.chdir(PROJNAME)
            res = runner.invoke(Cli, ['domain', 'foobar'])
            assert res.exit_code == 2

        with runner.isolated_filesystem():
            res = runner.invoke(Cli, ['init', PROJNAME])
            os.chdir(PROJNAME)
            res = runner.invoke(Cli, ['domain', '--help'])
            assert r.exit_code == 0

        with runner.isolated_filesystem():
            res = runner.invoke(Cli, ['init', PROJNAME])
            os.chdir(PROJNAME)
            res = runner.invoke(Cli, ['domain', 'create', '--help'])
            assert r.exit_code == 0

        with runner.isolated_filesystem():
            res = runner.invoke(Cli, ['init', PROJNAME])
            os.chdir(PROJNAME)
            res = runner.invoke(Cli, ['domain', 'read', '--help'])
            assert r.exit_code == 0

        with runner.isolated_filesystem():
            res = runner.invoke(Cli, ['init', PROJNAME])
            os.chdir(PROJNAME)
            res = runner.invoke(Cli, ['domain', 'update', '--help'])
            assert r.exit_code == 0

        with runner.isolated_filesystem():
            res = runner.invoke(Cli, ['init', PROJNAME])
            os.chdir(PROJNAME)
            res = runner.invoke(Cli, ['domain', 'delete', '--help'])
            assert r.exit_code == 0

    def test_domain_create(self, runner, dropdb):
        with runner.isolated_filesystem():
            res = runner.invoke(Cli, ['init', PROJNAME])
            assert res.exit_code == 0

            os.chdir(PROJNAME)
            
            DOMNAME='tmp_domain'
            res = runner.invoke(Cli, ['domain', 'create', DOMNAME])
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
