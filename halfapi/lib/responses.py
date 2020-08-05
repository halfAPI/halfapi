#!/usr/bin/env python3
# builtins
import numbers
import csv
from datetime import date
from io import TextIOBase, StringIO
from half_orm.null import NULL

# asgi framework
from starlette.responses import PlainTextResponse, Response, JSONResponse

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

class HJSONResponse(JSONResponse):
    def __init__(self, obj):
        obj = self.__serialize(obj)
        super().__init__(
            content=obj,
            status_code = 200)

    def __serialize(self, obj):
        if isinstance(obj, dict):
            robj = dict()
            for key, value in obj.items():
                robj[key] = self.__serialize(value)
            return robj
        if isinstance(obj, list):
            robj = []
            for value in obj:
                robj.append(self.__serialize(value))
            return robj
        if isinstance(obj, numbers.Number) or isinstance(obj, str):
            return obj
        if obj == NULL:
            return None
        return str(obj)
