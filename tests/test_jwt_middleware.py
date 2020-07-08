import jwt
import requests
import pytest
import json
import sys
from hashlib import sha256
from halfapi.app import app
from base64 import b64decode

def coucou():
    return 
def test_connected():
    app.route('/', coucou)

def test_token():
    # This test needs to have a running auth-lirmm on 127.0.0.1:3000

    r = requests.post('http://127.0.0.1:3000/',
        data={'email':'maizi', 'password':'a'})

    assert len(r.text) > 0
    res = json.loads(r.text)
    assert 'token' in res.keys()
    sys.stderr.write(f'Token : {res["token"]}\n')
    secret = open('/etc/half_orm/secret').readline()
    sys.stderr.write(f'Secret : {secret}\n')
    assert jwt.decode(
        res['token'],
        secret, algorithms=['HS256'])
