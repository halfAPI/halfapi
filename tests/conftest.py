#!/usr/bin/env python3
import logging
import functools
import re
import os
import subprocess
import importlib
import tempfile
from typing import Dict, Tuple
from uuid import uuid1, uuid4, UUID
from click.testing import CliRunner
import jwt
import sys
from unittest.mock import patch
import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.testclient import TestClient
from halfapi import __version__
from halfapi.halfapi import HalfAPI
from halfapi.cli.cli import cli
from halfapi.cli.init import init
from halfapi.cli.domain import domain, create_domain
from halfapi.lib.responses import ORJSONResponse
from halfapi.lib.jwt_middleware import JWTAuthenticationBackend

logger = logging.getLogger()

PROJNAME = os.environ.get('PROJ','tmp_api')

SECRET = 'dummysecret'

from halfapi.lib.jwt_middleware import (
    JWTUser, JWTAuthenticationBackend,
    JWTWebSocketAuthenticationBackend)

@pytest.fixture
def dummy_domain():
    yield {
        'name': 'dummy_domain',
        'router': '.routers',
        'enabled': True,
        'prefix': False,
        'config': {
            'test': True
        }
    }

@pytest.fixture
def token_builder():
    yield jwt.encode({
        'name':'xxx',
        'user_id': str(uuid4())},
        key=SECRET
    )

@pytest.fixture
def token_debug_false_builder():
    yield jwt.encode({
        'name':'xxx',
        'user_id': str(uuid4()),
        'debug': False},
        key=SECRET
    )


@pytest.fixture
def token_debug_true_builder():
    yield jwt.encode({
        'name':'xxx',
        'user_id': str(uuid4()),
        'debug': True},
        key=SECRET
    )

@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli_runner():
    """Yield a click.testing.CliRunner to invoke the CLI."""
    class_ = CliRunner

    def invoke_wrapper(f):
        """Augment CliRunner.invoke to emit its output to stdout.

        This enables pytest to show the output in its logs on test
        failures.

        """
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            echo = kwargs.pop('echo', False)
            result = f(*args, **kwargs)

            if echo is True:
                sys.stdout.write(result.output)

            return result

        return wrapper

    class_.invoke = invoke_wrapper(class_.invoke)
    cli_runner_ = class_()

    yield cli_runner_

@pytest.fixture
def halfapicli(cli_runner):
    def caller(*args):
        return cli_runner.invoke(cli, ' '.join(args))

    yield caller


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
def project_runner(runner, halfapicli, tree):
    with runner.isolated_filesystem():
        res = halfapicli('init', PROJNAME)

        os.chdir(PROJNAME)

        fs_path = os.getcwd()
        sys.path.insert(0, fs_path)

        secret = tempfile.mkstemp()
        SECRET_PATH = secret[1]
        with open(SECRET_PATH, 'w') as f:
            f.write(str(uuid1()))

        """
        with open(os.path.join('.halfapi', PROJNAME), 'w') as halfapi_etc:
            PROJ_CONFIG = re.sub('secret = .*', f'secret = {SECRET_PATH}',
                format_halfapi_etc(PROJNAME, os.getcwd()))
            halfapi_etc.write(PROJ_CONFIG)
        """


        ###
        # add dummy domain
        ###
        create_domain('test_domain', 'test_domain.routers')
        ###

        yield halfapicli

        while fs_path in sys.path:
            sys.path.remove(fs_path)

@pytest.fixture
def dummy_app():
    app = Starlette()
    app.add_route('/',
        lambda request, *args, **kwargs: PlainTextResponse('Hello test!'))
    app.add_middleware(
        AuthenticationMiddleware,
        backend=JWTAuthenticationBackend(secret_key='dummysecret')
    )
    return app

@pytest.fixture
def dummy_debug_app():
    app = Starlette(debug=True)
    app.add_route('/',
        lambda request, *args, **kwargs: PlainTextResponse('Hello test!'))
    app.add_middleware(
        AuthenticationMiddleware,
        backend=JWTAuthenticationBackend(secret_key='dummysecret')
    )
    return app


@pytest.fixture
def test_client(dummy_app):
    return TestClient(dummy_app)

@pytest.fixture
def create_route():
    def wrapped(domain_path, method, path):
        stack = [domain_path, *path.split('/')[1:]]
        for i in range(len(stack)):
            if len(stack[i]) == 0:
                continue

            path = os.path.join(*stack[0:i+1])
            if os.path.isdir(os.path.join(path)):
                continue
            os.mkdir(path)
        init_path = os.path.join(*stack, '__init__.py')
        with open(init_path, 'a+') as f:
            f.write(f'\ndef {method}():\n    raise NotImplementedError')

    return wrapped



@pytest.fixture
def dummy_project():
    halfapi_config = tempfile.mktemp()
    halfapi_secret = tempfile.mktemp()
    domain = 'dummy_domain'

    with open(halfapi_config, 'w') as f:
        f.writelines([
            '[project]\n',
            'name = lirmm_api\n',
            'halfapi_version = 0.5.0\n',
            f'secret = {halfapi_secret}\n',
            'port = 3050\n',
            'loglevel = debug\n',
            '[domain.dummy_domain]\n',
            f'name = {domain}\n',
            'router = dummy_domain.routers\n',
            f'[domain.dummy_domain.config]\n',
            'test = True'
        ])

    with open(halfapi_secret, 'w') as f:
        f.write('turlututu')

    return (halfapi_config, 'dummy_domain', 'dummy_domain.routers')

@pytest.fixture
def application_debug(project_runner):
    halfAPI = HalfAPI({
        'secret':'turlututu',
        'production':False,
        'domain': {
            'dummy_domain': {
                'name': 'test_domain',
                'router': 'test_domain.routers',
                'enabled': True,
                'prefix': False,
                'config':{
                    'test': True
                }
            }
        },
    })

    assert isinstance(halfAPI, HalfAPI)
    yield halfAPI.application


@pytest.fixture
def application_domain(dummy_domain):
    return HalfAPI({
        'secret':'turlututu',
        'production':True,
        'domain': {
            'dummy_domain': {
                **dummy_domain,
                'config': {
                    'test': True
                }
            }
        }
    }).application


@pytest.fixture
def tree():
    def wrapped(path):
        list_dirs = os.walk(path)
        for root, dirs, files in list_dirs:
            for d in dirs:
                print(os.path.join(root, d))
            for f in files:
                print(os.path.join(root, f))
    return wrapped
