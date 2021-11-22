from halfapi.halfapi import HalfAPI

def test_conf_production_default():
    halfapi = HalfAPI({
        'DOMAINS': {'test': True}
    })
    assert halfapi.PRODUCTION is True

def test_conf_production_true():
    halfapi = HalfAPI({
        'PRODUCTION': True,
        'DOMAINS': {'test': True}
    })
    assert halfapi.PRODUCTION is True

def test_conf_production_false():
    halfapi = HalfAPI({
        'PRODUCTION': False,
        'DOMAINS': {'test': True}
    })
    assert halfapi.PRODUCTION is False

