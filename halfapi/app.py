import os
from .halfapi import HalfAPI
from .logging import logger

def application():
    from .conf import CONFIG
    return HalfAPI(CONFIG).application
