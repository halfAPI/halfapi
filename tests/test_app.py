import os
from starlette.applications import Starlette
from unittest.mock import MagicMock, patch
from halfapi.halfapi import HalfAPI

from halfapi.lib.domain import NoDomainsException

def test_halfapi_dummy_domain(dummy_domain):
    with patch('starlette.applications.Starlette') as mock:
        mock.return_value = MagicMock()
        config = {}
        config['domain'] = {}
        config['domain'][dummy_domain['name']] = dummy_domain
        print(config)
        halfapi = HalfAPI(config)
