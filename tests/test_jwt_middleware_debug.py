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


#from halfapi.app import app
os.environ['HALFAPI_PROD'] = ''
os.environ['HALFAPI_SECRET'] = 'randomsecret'

from halfapi.lib.jwt_middleware import (PRODUCTION, SECRET,
    JWTUser, JWTAuthenticationBackend,
    JWTWebSocketAuthenticationBackend)

def test_constants():
    assert PRODUCTION == bool(os.environ['HALFAPI_PROD'])
    #assert SECRET == os.environ['HALFAPI_SECRET']


@pytest.fixture
def token_debug_builder():
    yield jwt.encode({
        'name':'xxx',
        'user_id': str(uuid4()),
        'debug': True},
        key=SECRET
    )


@pytest.mark.asyncio
async def test_JWTAuthenticationBackend_debug(token_debug_builder):
    backend = JWTAuthenticationBackend()

    req = Request(
        headers={
            'Authorization': token_debug_builder
        })

    auth = await backend.authenticate(req)
    assert(len(auth) == 2) 
    assert type(auth[0]) == AuthCredentials
    assert type(auth[1]) == JWTUser
