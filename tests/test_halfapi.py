from halfapi.halfapi import HalfAPI

def test_methods():
    assert 'application' in dir(HalfAPI)
    assert 'version' in dir(HalfAPI)
    assert 'version_async' in dir(HalfAPI)
