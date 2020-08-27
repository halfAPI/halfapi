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
os.environ['HALFAPI_PROD'] = 'True'
os.environ['HALFAPI_SECRET'] = 'randomsecret'

from halfapi.lib.jwt_middleware import (PRODUCTION, SECRET,
    JWTUser, JWTAuthenticationBackend,
    JWTWebSocketAuthenticationBackend)

def test_constants():
    assert PRODUCTION == bool(os.environ['HALFAPI_PROD'])
    assert SECRET == os.environ['HALFAPI_SECRET']

@pytest.fixture
def token():
    # This fixture needs to have a running auth-lirmm on 127.0.0.1:3000
    # Sets a valid token

    r = requests.post('http://127.0.0.1:3000/',
        data={'email':'maizi', 'password':'a'})

    if len(r.text) <= 0:
        raise Exception('No result in token retrieval')

    try:
        res = json.loads(r.text)
    except JSONDecodeError:
        raise Exception('Malformed response from token retrieval')

    if 'token' not in res.keys():
        raise Exception('Missing token in token request')

    return res['token']


@pytest.fixture
def token_builder():
    yield jwt.encode({
        'name':'xxx',
        'id': str(uuid4())},
        key=SECRET
    )


@pytest.fixture
def token_dirser():
    # This fixture needs to have a running auth-lirmm on 127.0.0.1:3000
    # Sets a valid token

    r = requests.post('http://127.0.0.1:3000/',
        data={'email':'dhenaut', 'password':'a'})

    if len(r.text) <= 0:
        raise Exception('No result in token retrieval')

    try:
        res = json.loads(r.text)
    except JSONDecodeError:
        raise Exception('Malformed response from token retrieval')

    if 'token' not in res.keys():
        raise Exception('Missing token in token request')

    return res['token']


"""
def test_token(token):
    client = TestClient(app)

    r = client.get('/user', headers={'Authorization':token})
    res = False
    try:
        res = json.loads(r.text)
    except JSONDecodeError:
        raise Exception('Malformed response from /user request')

    assert 'user' in res.keys()
    assert 'id' in res['user'].keys()
    assert 'token' in res['user'].keys()
    assert 'payload' in res['user'].keys()

def test_labopers(token, token_dirser):
    res = requests.get('http://127.0.0.1:8080/api/v4/organigramme/laboratoire/personnel',
        params={
            'q': 'limit:10|format:csv'
        },
        headers={
            'Authorization': token
        })

    assert res.status_code == 401

    res = requests.get('http://127.0.0.1:8080/api/v4/organigramme/laboratoire/personnel',
        params={
            'q': 'limit:10|format:csv'
        },
        headers={
            'Authorization': token_dirser
        })

    assert res.status_code == 200
"""

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
async def test_JWTAuthenticationBackend(token_builder):
    backend = JWTAuthenticationBackend()
    assert backend.secret_key == SECRET

    req = Request(
        headers={
            'Authorization': token_builder
        })

    credentials, user = await backend.authenticate(req)
    assert type(user) == JWTUser
    assert type(credentials) == AuthCredentials
