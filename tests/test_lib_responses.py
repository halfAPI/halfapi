import json
import decimal
import datetime

from starlette.responses import Response
from halfapi.lib.responses import *

def test_orjson():
    test_obj = {
        "ok": "ko",
        "dec": decimal.Decimal(42),
        "set": {0, 4, 2},
        "date": datetime.date(1,1,1),
        "datetime": datetime.datetime(1,1,1),
    }

    resp = ORJSONResponse(test_obj)
    body = resp.body.decode()
    test_obj_dec = json.loads(body)
    print(test_obj_dec)
    assert 'ok' in test_obj_dec.keys()
    assert isinstance(test_obj_dec['ok'], str)
    assert isinstance(test_obj_dec['dec'], str)
    assert isinstance(test_obj_dec['set'], list)
    assert isinstance(test_obj_dec['date'], str)
    assert test_obj_dec['date'] == '0001-01-01'
    assert test_obj_dec['datetime'] == '0001-01-01T00:00:00'


def test_responses():
    resp = HJSONResponse('')
    assert isinstance(resp, Response)
    assert resp.status_code == 200

    resp = ORJSONResponse('')
    assert isinstance(resp, Response)
    assert resp.status_code == 200

    resp = PlainTextResponse()
    assert isinstance(resp, Response)
    assert resp.status_code == 200

def test_errors():
    resp = ServiceUnavailableResponse()
    assert isinstance(resp, Response)
    assert resp.status_code == 503

    resp = UnauthorizedResponse()
    assert isinstance(resp, Response)
    assert resp.status_code == 401

    resp = InternalServerErrorResponse()
    assert isinstance(resp, Response)
    assert resp.status_code == 500

    resp = NotFoundResponse()
    assert isinstance(resp, Response)
    assert resp.status_code == 404

    resp = NotImplementedResponse()
    assert isinstance(resp, Response)
    assert resp.status_code == 501
