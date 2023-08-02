import os
from .halfapi import HalfAPI
from .logging import logger
from .conf import read_config

def application():
    config_file = os.environ.get('HALFAPI_CONF_FILE', '.halfapi/config')

    CONFIG = read_config([config_file])

    return HalfAPI(CONFIG).application
