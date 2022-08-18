import pytest
from click.testing import CliRunner
from halfapi.cli.cli import cli
import os
from unittest.mock import patch


@pytest.mark.skip
def test_run_noproject(cli_runner):
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(cli, ['config'])
        print(result.stdout)
        assert result.exit_code == 0

        result = cli_runner.invoke(cli, ['run', '--dryrun'])
        try:
            assert result.exit_code == 0
        except AssertionError as exc:
            print(result.stdout)
            raise exc

"""
def test_run_empty_project(cli_runner):
    with cli_runner.isolated_filesystem():
        os.mkdir('dummy_domain')
        result = cli_runner.invoke(cli, ['run', './dummy_domain'])
        assert result.exit_code == 1

def test_run_dummy_project(project_runner):
    with patch('uvicorn.run', autospec=True) as runMock:
        result = project_runner.invoke(cli, ['run'])
        runMock.assert_called_once()
"""
