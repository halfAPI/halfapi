from halfapi.cli.cli import cli
from configparser import ConfigParser

def test_config(cli_runner):
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(cli, ['config'])
        cp = ConfigParser()
        cp.read_string(result.output)
        assert cp.has_section('project')
