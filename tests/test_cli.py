#!/usr/bin/env python3
import os

import pytest
from click.testing import CliRunner

from halfapi.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_cli(runner):
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
        r = runner.invoke(cli, ['dbupdate', '--help'])
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

    with runner.isolated_filesystem():
        r = runner.invoke(cli, ['routes', '--help'])
        assert r.exit_code == 0
