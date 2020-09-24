#!/usr/bin/env python3
import pytest
from starlette.authentication import UnauthenticatedUser
from starlette.testclient import TestClient
from halfapi.app import application
import json

def test_itworks():
    c = TestClient(application)
    r = json.loads(c.get('/').text)
    assert r == 'It Works!'

def test_user():
    c = TestClient(application)
    r = c.get('/user')
    assert r.status_code == 200

def test_user():
    c = TestClient(application)
    r = c.get('/schema')
    assert r.status_code == 200
