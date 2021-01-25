import json
import decimal

from halfapi.lib.responses import ORJSONResponse


def test_orjson():
    test_obj = {
        "ok": "ko",
        "dec": decimal.Decimal(42),
        "set": {0, 4, 2}
    }

    resp = ORJSONResponse(test_obj)
    body = resp.body.decode()
    test_obj_dec = json.loads(body)
    print(test_obj_dec)
    assert 'ok' in test_obj_dec.keys()
    assert isinstance(test_obj_dec['ok'], str)
    assert isinstance(test_obj_dec['dec'], str)
    assert isinstance(test_obj_dec['set'], list)
