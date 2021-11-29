from halfapi.halfapi import HalfAPI

def test_conf_production_default():
    halfapi = HalfAPI({
        'domains': {'test': True}
    })
    assert halfapi.PRODUCTION is True

def test_conf_production_true():
    halfapi = HalfAPI({
        'production': True,
        'domains': {'test': True}
    })
    assert halfapi.PRODUCTION is True

def test_conf_production_false():
    halfapi = HalfAPI({
        'production': False,
        'domains': {'test': True}
    })
    assert halfapi.PRODUCTION is False

def test_conf_variables():
    from halfapi.conf import (
        CONFIG,
        SCHEMA,
        SECRET,
        DOMAINSDICT,
        PROJECT_NAME,
        HOST,
        PORT,
        CONF_DIR
    )

    assert isinstance(CONFIG, dict)
    assert isinstance(SCHEMA, dict)
    assert isinstance(SECRET, str)
    assert isinstance(DOMAINSDICT(), dict)
    assert isinstance(PROJECT_NAME, str)
    assert isinstance(HOST, str)
    assert isinstance(PORT, str)
    assert str(int(PORT)) == PORT
    PORT = 'abc'
    assert str(int(PORT)) == PORT
    assert isinstance(CONF_DIR, str)
