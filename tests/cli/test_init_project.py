#!/usr/bin/env python3
import os
import subprocess

import pytest
from click.testing import CliRunner

from halfapi import __version__
from halfapi.cli import cli
from configparser import ConfigParser

projname = os.environ.get('PROJ','tmp_api')

@pytest.fixture
def dropdb():
    p = subprocess.Popen(['dropdb', f'halfapi_{projname}'])
    p.wait()
    yield 

    p = subprocess.Popen(['dropdb', f'halfapi_{projname}'])
    p.wait()
    
def test_init_project(dropdb):
    runner = CliRunner()
    cp = ConfigParser()
    with runner.isolated_filesystem():
        env = {
            'HALFORM_CONF_DIR': os.environ.get('HALFORM_CONF_DIR', os.getcwd()),
            'HALFAPI_CONF_DIR': os.environ.get('HALFAPI_CONF_DIR', os.getcwd()),
        }

        res = runner.invoke(cli, ['init-project', projname], env=env)
        try:
            assert os.path.isdir(projname)
            assert os.path.isdir(os.path.join(projname, '.halfapi'))


            # .halfapi/config check
            assert os.path.isfile(os.path.join(projname, '.halfapi', 'config'))
            cp.read(os.path.join(projname, '.halfapi', 'config'))
            assert cp.has_section('project')
            assert cp.has_option('project', 'name')
            assert cp.get('project', 'name') == projname
            assert cp.get('project', 'halfapi_version') == __version__

            # .halfapi/domains check
            assert os.path.isfile(os.path.join(projname, '.halfapi', 'domains'))
            cp.read(os.path.join(projname, '.halfapi', 'domains'))
            assert cp.has_section('domains')
        except AssertionError:
            subprocess.run(['tree', '-a', os.getcwd()])

        assert res.exit_code == 0
        assert res.exception is None


