from halfapi.halfapi import HalfAPI

halfapi_arg = { 'domain': { 'name': 'dummy_domain', 'router': 'routers' } }
def test_conf_production_default():
    halfapi = HalfAPI({
        **halfapi_arg
    })
    assert halfapi.PRODUCTION is True

def test_conf_production_true():
    halfapi = HalfAPI({
        **halfapi_arg,
        'production': True,
    })
    assert halfapi.PRODUCTION is True

def test_conf_production_false():
    halfapi = HalfAPI({
        **halfapi_arg,
        'production': False,
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
    assert isinstance(CONF_DIR, str)
