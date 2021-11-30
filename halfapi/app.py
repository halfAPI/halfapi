from .halfapi import HalfAPI
from .conf import CONFIG, SCHEMA
from .logging import logger

logger.info('CONFIG: %s', CONFIG)
logger.info('SCHEMA: %s', SCHEMA)

application = HalfAPI(
    CONFIG, SCHEMA or None).application
