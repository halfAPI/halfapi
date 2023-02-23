import importlib
from halfapi.testing.test_domain import TestDomain

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
    from .dummy_domain.routers.config import get
    from .dummy_domain.routers import async_router
    from .dummy_domain.routers.async_router import ROUTES, get_abc_alphabet_TEST, get_abc_pinnochio, get_config, get_arguments
