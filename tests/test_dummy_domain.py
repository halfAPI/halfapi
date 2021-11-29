def test_dummy_domain():
    from . import dummy_domain
    from .dummy_domain import acl
    assert acl.public() is True
    assert isinstance(acl.random(), int)
    assert acl.denied() is False
