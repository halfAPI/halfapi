import os
from starlette.applications import Starlette
from unittest.mock import MagicMock, patch
from halfapi.halfapi import HalfAPI

from halfapi.lib.domain import NoDomainsException

def test_halfapi_dummy_domain():
    with patch('starlette.applications.Starlette') as mock:
        mock.return_value = MagicMock()
        halfapi = HalfAPI({
            'DOMAINS': {
                'dummy_domain': '.routers'
            }
        })