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

@pytest.mark.asyncio
async def test_JWTAuthenticationBackend_NoToken(token_builder):
    backend = JWTAuthenticationBackend()
    assert backend.secret_key == SECRET

    req = Request()

    credentials, user = await backend.authenticate(req)
    assert isinstance(user, UnauthenticatedUser)
    assert isinstance(credentials, AuthCredentials)


@pytest.mark.asyncio
async def test_JWTAuthenticationBackend_Token(token_builder):
    backend = JWTAuthenticationBackend()
    assert backend.secret_key == SECRET

    req = Request(
        headers={
            'Authorization': token_builder
        })

    credentials, user = await backend.authenticate(req)
    assert isinstance(user, JWTUser)
    assert isinstance(credentials, AuthCredentials)


@pytest.mark.asyncio
async def test_JWTAuthenticationBackend_DebugFalse(token_debug_false_builder):
    backend = JWTAuthenticationBackend()
    assert backend.secret_key == SECRET

    req = Request(
        headers={
            'Authorization': token_debug_false_builder
        })

    credentials, user = await backend.authenticate(req)
    assert isinstance(user, JWTUser)
    assert isinstance(credentials, AuthCredentials)


@pytest.mark.asyncio
async def test_JWTAuthenticationBackend_DebugTrue(token_debug_true_builder):
    backend = JWTAuthenticationBackend()
    assert backend.secret_key == SECRET

    req = Request(
        headers={
            'Authorization': token_debug_true_builder
        })

    try:
        await backend.authenticate(req)
    except Exception as exc:
        assert type(exc) == AuthenticationError

@pytest.mark.asyncio
async def test_JWTAuthenticationBackend_Check(token_debug_false_builder):
    backend = JWTAuthenticationBackend()
    assert backend.secret_key == SECRET

    req = Request(
        params={
            'check':True,
        })

    credentials, user = await backend.authenticate(req)
    assert isinstance(user, UnauthenticatedUser)
    assert isinstance(credentials, AuthCredentials)


@pytest.mark.asyncio
async def test_JWTAuthenticationBackend_CheckUserId(token_debug_false_builder):
    backend = JWTAuthenticationBackend()
    assert backend.secret_key == SECRET

    tmp_user_id = str(uuid4())

    req = Request(
        params={
            'check': True,
            'user_id': tmp_user_id
        })

    credentials, user = await backend.authenticate(req)
    assert isinstance(user, JWTUser)
    assert user.__id ==  tmp_user_id
    assert isinstance(credentials, AuthCredentials)
