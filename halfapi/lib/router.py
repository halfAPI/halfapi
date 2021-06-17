import os
from types import ModuleType
from typing import Dict

from halfapi.lib.constants import VERBS

def read_router(m_router: ModuleType) -> Dict:
    """
    Reads a module and returns a router dict
    """

    if not hasattr(m_router, 'ROUTES'):
        routes = {'':{}}
        acls = getattr(m_router, 'ACLS') if hasattr(m_router, 'ACLS') else None

        if acls is not None:
            for verb in VERBS:
                if not hasattr(m_router, verb.lower()):
                    continue

                """ There is a "verb" route in the router
                """

                if verb.upper() not in acls:
                    continue

                routes[''][verb.upper()] = []
                routes[''][verb.upper()] = acls[verb.upper()].copy()

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

    return routes
