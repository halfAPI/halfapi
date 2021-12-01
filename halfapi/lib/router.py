import os
import sys
import subprocess
from types import ModuleType
from typing import Dict
from pprint import pprint

from schema import SchemaError
from .constants import VERBS, ROUTER_SCHEMA
from ..logging import logger

def read_router(m_router: ModuleType) -> Dict:
    """
    Reads a module and returns a router dict

    If the module has a "ROUTES" constant, it just returns this constant,
    Else, if the module has an "ACLS" constant, it builds the accurate dict

    TODO: May be another thing, may be not a part of halfAPI

    """
    m_path = None

    try:
        if not hasattr(m_router, 'ROUTES'):
            routes = {'':{}}
            acls = getattr(m_router, 'ACLS') if hasattr(m_router, 'ACLS') else None

            if acls is not None:
                for method in acls.keys():
                    if method not in VERBS:
                        raise Exception(
                            'This method is not handled: {}'.format(method))

                    routes[''][method] = []
                    routes[''][method] = acls[method].copy()

            routes['']['SUBROUTES'] = []
            if hasattr(m_router, '__path__'):
                """ Module is a package
                """
                m_path = getattr(m_router, '__path__')
                if isinstance(m_path, list) and len(m_path) == 1:
                    routes['']['SUBROUTES'] = [
                        elt.name
                        for elt in os.scandir(m_path[0])
                        if elt.is_dir()
                    ]
        else:
            routes = getattr(m_router, 'ROUTES')

        try:
            ROUTER_SCHEMA.validate(routes)
        except SchemaError as exc:
            logger.error(routes)
            raise exc

        return routes
    except ImportError as exc:
        # TODO: Proper exception handling
        raise exc
    except FileNotFoundError as exc:
        # TODO: Proper exception handling
        logger.error(m_path)
        raise exc
