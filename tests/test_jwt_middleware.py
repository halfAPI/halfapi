import os
import jwt
from requests import Request
import pytest
from unittest.mock import patch
import json
from json.decoder import JSONDecodeError
import sys
from hashlib import sha256
from base64 import b64decode
from uuid import uuid4, UUID

from starlette.testclient import TestClient
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, BaseUser, AuthCredentials,
    UnauthenticatedUser)
from starlette.responses import PlainTextResponse

from halfapi.lib.jwt_middleware import (
    JWTUser, JWTAuthenticationBackend,
    JWTWebSocketAuthenticationBackend)


def test_JWTUser():
    uid = uuid4()
    token = '{}'
    payload = {}
    user = JWTUser(uid, token, payload)
    assert user.id == uid
    assert user.token == token
    assert user.payload == payload
    assert user.is_authenticated == True

def test_jwt_NoToken(dummy_app):
    async def test_route(request):
        assert isinstance(request.user, UnauthenticatedUser)
        return PlainTextResponse('ok')

    dummy_app.add_route('/test', test_route)
    test_client = TestClient(dummy_app)
    resp = test_client.request('get', '/test')
    assert resp.status_code == 200

def test_jwt_Token(dummy_app, token_builder):
    async def test_route(request):
        assert isinstance(request.user, JWTUser)
        print(request.scope['app'].debug)
        return PlainTextResponse('ok')

    dummy_app.add_route('/test', test_route)
    test_client = TestClient(dummy_app)

    resp = test_client.request('get', '/test',
        cookies={
            'Authorization': token_builder
        })
    assert resp.status_code == 200

    resp = test_client.request('get', '/test',
        headers={
            'Authorization': token_builder
        })
    assert resp.status_code == 200



def test_jwt_DebugFalse(dummy_app, token_debug_false_builder):
    async def test_route(request):
        assert isinstance(request.user, JWTUser)
        return PlainTextResponse('ok')

    dummy_app.add_route('/test', test_route)
    test_client = TestClient(dummy_app)

    resp = test_client.request('get', '/test',
        cookies={
            'Authorization': token_debug_false_builder
        })
    assert resp.status_code == 200

    resp = test_client.request('get', '/test',
        headers={
            'Authorization': token_debug_false_builder
        })
    assert resp.status_code == 200


def test_jwt_DebugTrue(dummy_app, token_debug_true_builder):
    """
    A debug token should return a 400 status code with a non debug app
    """
    async def test_route(request):
        return PlainTextResponse('ok')

    dummy_app.add_route('/test', test_route)
    test_client = TestClient(dummy_app)

    resp = test_client.request('get', '/test',
        cookies={
            'Authorization': token_debug_true_builder
        })
    assert resp.status_code == 400

    resp = test_client.request('get', '/test',
        headers={
            'Authorization': token_debug_true_builder
        })
    assert resp.status_code == 400


def test_jwt_DebugTrue_DebugApp(dummy_debug_app, token_debug_true_builder):
    """
    A debug token should return a 200 status code with a debug app
    """
    async def test_route(request):
        assert isinstance(request.user, JWTUser)
        return PlainTextResponse('ok')

    dummy_debug_app.add_route('/test', test_route)
    test_client = TestClient(dummy_debug_app)

    resp = test_client.request('get', '/test',
        cookies={
              'Authorization': token_debug_true_builder
        })
    assert resp.status_code == 200

    resp = test_client.request('get', '/test',
        headers={
              'Authorization': token_debug_true_builder
        })
    assert resp.status_code == 200
