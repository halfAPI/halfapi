#!/usr/bin/env python3
import os
import subprocess

import pytest
from click.testing import CliRunner
from configparser import ConfigParser

from halfapi import __version__
from halfapi.cli import cli

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


@pytest.mark.incremental
class TestCli():
    def test_options(self, runner, dropdb):
        # Wrong command
        with runner.isolated_filesystem():
            r = runner.invoke(cli, ['foobar'])
            assert r.exit_code == 2

        # Test existing commands
        with runner.isolated_filesystem():
            r = runner.invoke(cli, ['--help'])
            assert r.exit_code == 0

        with runner.isolated_filesystem():
            r = runner.invoke(cli, ['--version'])
            assert r.exit_code == 0

        with runner.isolated_filesystem():
            r = runner.invoke(cli, ['init-project', '--help'])
            assert r.exit_code == 0

        with runner.isolated_filesystem():
            r = runner.invoke(cli, ['run', '--help'])
            assert r.exit_code == 0

        with runner.isolated_filesystem():
            r = runner.invoke(cli, ['domain', '--help'])
            assert r.exit_code == 0


    def test_init_project_fail(self, runner, dropdb):
        # Missing argument (project)
        testproject = 'testproject'
        r = runner.invoke(cli, ['init-project'])
        assert r.exit_code == 2

        with runner.isolated_filesystem():
            # Fail : Wrong project name
            r = runner.invoke(cli, ['init-project', 'test*-project'])
            assert r.exit_code == 1

        with runner.isolated_filesystem():
            # Fail : Already existing folder
            os.mkdir(testproject)
            r = runner.invoke(cli, ['init-project', testproject])
            assert r.exit_code == 1

        with runner.isolated_filesystem():
            # Fail : Already existing nod
            os.mknod(testproject)
            r = runner.invoke(cli, ['init-project', testproject])
            assert r.exit_code == 1

    def test_init_project(self, runner, dropdb):
        cp = ConfigParser()
        with runner.isolated_filesystem():
            env = {
                'HALFORM_CONF_DIR': os.environ.get('HALFORM_CONF_DIR', os.getcwd()),
                'HALFAPI_CONF_DIR': os.environ.get('HALFAPI_CONF_DIR', os.getcwd()),
            }

            res = runner.invoke(cli, ['init-project', PROJNAME], env=env)
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


    def test_domain_commands(self, runner, dropdb):
        with runner.isolated_filesystem():
            res = runner.invoke(cli, ['domain', 'foobar'])
            assert res.exit_code == 2

        with runner.isolated_filesystem():
            res = runner.invoke(cli, ['domain', 'create', '--help'])
            assert r.exit_code == 0

        with runner.isolated_filesystem():
            res = runner.invoke(cli, ['domain', 'read', '--help'])
            assert r.exit_code == 0

        with runner.isolated_filesystem():
            res = runner.invoke(cli, ['domain', 'update', '--help'])
            assert r.exit_code == 0

        with runner.isolated_filesystem():
            res = runner.invoke(cli, ['domain', 'delete', '--help'])
            assert r.exit_code == 0
