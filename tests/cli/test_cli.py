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


def test_options(runner):
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


@pytest.mark.skip
def test_init_project_fail(runner):
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

@pytest.mark.skip
def test_init_project(runner):
    """
    """
    cp = ConfigParser()
    with runner.isolated_filesystem():
        env = {
            'HALFAPI_CONF_DIR': '.halfapi'
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
            # removal of domain section (0.6)
            # assert cp.has_section('domain')
        except AssertionError as exc:
            subprocess.run(['tree', '-a', os.getcwd()])
            raise exc

        assert res.exit_code == 0
        assert res.exception is None
