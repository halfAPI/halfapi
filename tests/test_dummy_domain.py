import importlib

def test_dummy_domain():
    from . import dummy_domain
    from .dummy_domain import acl
    assert acl.public() is True
    assert isinstance(acl.random(), int)
    assert acl.private() is False


    from .dummy_domain import routers
    from .dummy_domain.routers.arguments import get
    from .dummy_domain.routers.abc.alphabet.TEST_uuid import get
    from .dummy_domain.routers.abc.pinnochio import get
    from .dummy_domain.routers.config import get
    async_mod = importlib.import_module('dummy_domain.routers.async', '.')
    fcts = ['get_abc_alphabet_TEST', 'get_abc_pinnochio', 'get_config', 'get_arguments']
    for fct in fcts:
        getattr(async_mod, fct)
