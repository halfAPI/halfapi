#!/usr/bin/env python3
import pytest
from starlette.authentication import UnauthenticatedUser
from starlette.testclient import TestClient
import subprocess
import json
import os
import sys
import pprint
import openapi_spec_validator
import logging
logger = logging.getLogger()

from halfapi.lib.constants import API_SCHEMA


def test_halfapi_whoami(application_debug):
    # @TODO : If we use isolated filesystem multiple times that creates a bug.
    # So we use a single function with fixture "application debug"

    c = TestClient(application_debug)
    r = c.request('get', '/halfapi/whoami')
    assert r.status_code == 200

def test_halfapi_log(application_debug):
    # @TODO : If we use isolated filesystem multiple times that creates a bug.
    # So we use a single function with fixture "application debug"

    c = TestClient(application_debug)

    r = c.request('get', '/halfapi/log')
    assert r.status_code == 200

def test_halfapi_error_400(application_debug):
    # @TODO : If we use isolated filesystem multiple times that creates a bug.
    # So we use a single function with fixture "application debug"

    c = TestClient(application_debug)

    r = c.request('get', '/halfapi/error/400')
    assert r.status_code == 400

def test_halfapi_error_404(application_debug):
    # @TODO : If we use isolated filesystem multiple times that creates a bug.
    # So we use a single function with fixture "application debug"

    c = TestClient(application_debug)

    r = c.request('get', '/halfapi/error/404')
    assert r.status_code == 404

def test_halfapi_error_500(application_debug):
    # @TODO : If we use isolated filesystem multiple times that creates a bug.
    # So we use a single function with fixture "application debug"

    c = TestClient(application_debug)

    r = c.request('get', '/halfapi/error/500')
    assert r.status_code == 500

def test_schema(application_debug):
    c = TestClient(application_debug)

    r = c.request('get', '/')
    schema = r.json()
    assert isinstance(schema, dict)
    openapi_spec_validator.validate_spec(schema)
