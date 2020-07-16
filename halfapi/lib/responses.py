#!/usr/bin/env python3
# builtins
import csv
from datetime import date
from io import TextIOBase, StringIO

# asgi framework
from starlette.responses import PlainTextResponse, Response

__all__ = [
    'InternalServerErrorResponse',
    'NotFoundResponse',
    'NotImplementedResponse',
    'PlainTextResponse',
    'UnauthorizedResponse']


class InternalServerErrorResponse(Response):
    """ The 500 Internal Server Error default Response  
    """
    def __init__(self, *args, **kwargs):
        super().__init__(status_code=500)


class NotFoundResponse(Response):
    """ The 404 Not Found default Response  
    """
    def __init__(self, *args, **kwargs):
        super().__init__(status_code=404)


class NotImplementedResponse(Response):
    """ The 501 Not Implemented default Response  
    """
    def __init__(self, *args, **kwargs):
        super().__init__(status_code=501)


class UnauthorizedResponse(Response):
    """ The 401 Not Found default Response  
    """
    def __init__(self, *args, **kwargs):
        super().__init__(status_code = 401)

