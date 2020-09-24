#!/usr/bin/env python3
import re
import os
import subprocess
import importlib
import tempfile
from unittest.mock import patch
from typing import Dict, Tuple
import pytest
from uuid import uuid1
from click.testing import CliRunner
from halfapi import __version__
from halfapi.cli import cli
from halfapi.cli.init import format_halfapi_etc
Cli = cli.cli

PROJNAME = os.environ.get('PROJ','tmp_api')

@pytest.fixture
def runner():
    return CliRunner()

def halfapicli(runner):
    return lambda *args: runner.invoke(Cli, args)


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

def confdir(dirname):
    d = os.environ.get(dirname)
    if not d:
        os.environ[dirname] = tempfile.mkdtemp(prefix='halfapi_')
        return os.environ.get(dirname)
    if not os.path.isdir(d):
        os.mkdir(d)
    return d

@pytest.fixture
def halform_conf_dir():
    return confdir('HALFORM_CONF_DIR')

@pytest.fixture
def halfapi_conf_dir():
    return confdir('HALFAPI_CONF_DIR')

# store history of failures per test class name and per index in parametrize (if
# parametrize used)
_test_failed_incremental: Dict[str, Dict[Tuple[int, ...], str]] = {}


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        # incremental marker is used
        if call.excinfo is not None:
            # the test has failed
            # retrieve the class name of the test
            cls_name = str(item.cls)
            # retrieve the index of the test (if parametrize is used in
            # combination with incremental)
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, "callspec")
                else ()
            )
            # retrieve the name of the test function
            test_name = item.originalname or item.name
            # store in _test_failed_incremental the original name of the failed
            # test
            _test_failed_incremental.setdefault(cls_name, {}).setdefault(
                parametrize_index, test_name
            )


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        # retrieve the class name of the test
        cls_name = str(item.cls)
        # check if a previous test has failed for this class
        if cls_name in _test_failed_incremental:
            # retrieve the index of the test (if parametrize is used in
            # combination with incremental)
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, "callspec")
                else ()
            )
            # retrieve the name of the first test function to fail for this
            # class name and index
            test_name = _test_failed_incremental[cls_name].get(parametrize_index, None)
            # if name found, test has failed for the combination of class name &
            # test name
            if test_name is not None:
                pytest.xfail("previous test failed ({})".format(test_name))

@pytest.fixture
def project_runner(runner, halfapi_conf_dir):
    global Cli
    env = {
        'HALFAPI_CONF_DIR': halfapi_conf_dir
    }
    with runner.isolated_filesystem():
        res = runner.invoke(Cli, ['init', PROJNAME],
            env=env,
            catch_exceptions=True)
        assert res.exit_code == 0

        os.chdir(PROJNAME)
        secret = tempfile.mkstemp()
        SECRET_PATH = secret[1]
        with open(SECRET_PATH, 'w') as f:
            f.write(str(uuid1()))

        with open(os.path.join(halfapi_conf_dir, PROJNAME), 'w') as f:
            PROJ_CONFIG = re.sub('secret = .*', f'secret = {SECRET_PATH}',
                format_halfapi_etc(PROJNAME, os.getcwd()))
            f.write(PROJ_CONFIG)

        importlib.reload(cli)
        Cli = cli.cli
        yield halfapicli(runner)
