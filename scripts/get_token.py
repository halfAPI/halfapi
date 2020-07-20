#!/usr/bin/python3
import requests
import json

r = requests.post('http://127.0.0.1:3000/auth',
    data={'email':'dhenaut', 'password':'a'})
r_obj = json.loads(r.text)
token = r_obj['token']
print(token)
