#!/usr/bin/env python3
import os
import subprocess
import importlib
import tempfile
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from configparser import ConfigParser

from halfapi import __version__
from halfapi.cli import cli
Cli = cli.cli

PROJNAME = os.environ.get('PROJ','tmp_api')


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

    def test_init_project(self, runner, halfapi_conf_dir):
        """
        """
        cp = ConfigParser()
        with runner.isolated_filesystem():
            env = {
                'HALFAPI_CONF_DIR': halfapi_conf_dir
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
                assert cp.has_section('domains')
            except AssertionError as exc:
                subprocess.run(['tree', '-a', os.getcwd()])
                raise exc

            assert res.exit_code == 0
            assert res.exception is None
