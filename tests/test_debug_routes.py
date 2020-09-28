#!/usr/bin/env python3
import pytest
from starlette.authentication import UnauthenticatedUser
from starlette.testclient import TestClient
from halfapi.app import application
import json

def test_get_api_routes():
    c = TestClient(application)
    r = c.get('/')
    d_r = r.json()
    assert isinstance(d_r, dict)


def test_current_user():
    c = TestClient(application)
    r = c.get('/halfapi/current_user')
    assert r.status_code == 200
