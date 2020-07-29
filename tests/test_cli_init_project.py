#!/usr/bin/env python3
import os

import pytest
from click.testing import CliRunner

from halfapi.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_init_project(runner):
    # Missing argument (project)
    r = runner.invoke(cli, ['init-project'])
    assert r.exit_code == 2

    with runner.isolated_filesystem():
        # Fail : Wrong project name
        r = runner.invoke(cli, ['init-project', 'test*-project'])
        assert r.exit_code == 1

    with runner.isolated_filesystem():
        # Fail : Already existing folder
        os.mkdir('testproject')
        r = runner.invoke(cli, ['init-project', 'testproject'])
        assert r.exit_code == 1

    with runner.isolated_filesystem():
        # Fail : Already existing nod
        os.mknod('testproject')
        r = runner.invoke(cli, ['init-project', 'testproject'])
        assert r.exit_code == 1

    with runner.isolated_filesystem():
        # Success : New repo
        r = runner.invoke(cli, ['init-project', 'testproject'])
        assert r.exit_code == 0
        assert os.path.isdir('testproject')
        assert os.path.isdir('testproject/.git')

    with runner.isolated_filesystem():
        # Success : Cloned repo
        import pygit2
        pygit2.init_repository('testproject.git', bare=True)
        assert os.path.isdir('testproject.git')

        r = runner.invoke(cli, ['init-project', 'testproject', '--repo', './testproject.git'])
        assert r.exit_code == 0
        assert os.path.isdir('testproject')
        assert os.path.isdir('testproject/.git')
