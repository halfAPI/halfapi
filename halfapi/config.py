#!/usr/bin/env python3
from os import environ

# Configuration
CONFIG={}
CONFIG['DEBUG'] = environ.get('DEBUG', False)
CONFIG['DEBUG_ACL'] = environ.get('DEBUG_ACL', False)
CONFIG['HALFORM_SECRET'] = environ.get('HALFORM_SECRET', False)


