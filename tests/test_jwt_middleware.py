import jwt
import requests
import pytest
import json
from json.decoder import JSONDecodeError
import sys
from hashlib import sha256
from base64 import b64decode
from starlette.testclient import TestClient

from halfapi.app import app
from halfapi.lib.jwt_middleware import (JWTUser, JWTAuthenticationBackend,
    JWTWebSocketAuthenticationBackend)

def coucou():
    return 
def test_connected():
    app.route('/', coucou)

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


def test_token(token):
    client = TestClient(app)

    r = client.get('/user', headers={'Authorization':token})
    res = False
    try:
        res = json.loads(r.text)
    except JSONDecodeError:
        raise Exception('Malformed response from /user request')

    assert 'user' in res.keys()
    print(res['user'])
    assert 'id' in res['user'].keys()
    assert 'token' in res['user'].keys()
    assert 'payload' in res['user'].keys()
