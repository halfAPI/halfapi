from .halfapi import HalfAPI
from .conf import PRODUCTION, SECRET, DOMAINS, CONFIG

application = HalfAPI({
    'PRODUCTION': PRODUCTION,
    'SECRET': SECRET,
    'DOMAINS': DOMAINS,
    'CONFIG': CONFIG,
}).application
