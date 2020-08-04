#!/usr/bin/env python3
import os

import pytest
from click.testing import CliRunner

from halfapi import __version__
from halfapi.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_init_project(runner):
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

    with runner.isolated_filesystem():
        # Success : New repo
        r = runner.invoke(cli, ['init-project', testproject])
        assert r.exit_code == 0
        assert os.path.isdir(testproject)
        assert os.path.isdir(f'{testproject}/.git')
        assert os.path.isdir(f'{testproject}/.halfapi')
        domain_file = 'testproject/.halfapi/domain'
        assert os.path.isfile(domain_file)
        conf_file = 'testproject/.halfapi/config'
        assert os.path.isfile(conf_file)
        config = ConfigParser()
        config.read([conf_file])
        assert config.has_section('project')
        assert config.has_option('project', 'name')
        assert config.get('project', 'name') == testproject
        assert config.has_option('project', 'halfapi_version') == __version__


    with runner.isolated_filesystem():
        # Success : Cloned repo
        import pygit2
        pygit2.init_repository('testproject.git', bare=True)
        assert os.path.isdir('testproject.git')

        r = runner.invoke(cli, [
            'init-project', testproject, '--repo',
            f'./{testproject}.git'])
        assert r.exit_code == 0
        assert os.path.isdir(testproject)
        assert os.path.isdir('testproject/.git')
