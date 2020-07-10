#!/usr/bin/env python3
import pytest
from starlette.authentication import UnauthenticatedUser
from starlette.testclient import TestClient
from halfapi.app import app

def test_itworks():
    c = TestClient(app)
    r = c.get('/')
    assert r.text == 'It Works!'

def test_user():
    c = TestClient(app)
    r = c.get('/user')
    assert r.status_code == 200
