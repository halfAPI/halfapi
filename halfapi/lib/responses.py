#!/usr/bin/env python3
# builtins
""" Response module

Contains some base response classes

Classes :
    - HJSONResponse
    - InternalServerErrorResponse
    - NotFoundResponse
    - NotImplementedResponse
    - ORJSONResponse
    - PlainTextResponse
    - UnauthorizedResponse

"""
import decimal
import typing
import orjson

# asgi framework
from starlette.responses import PlainTextResponse, Response, JSONResponse


__all__ = [
    'HJSONResponse',
    'InternalServerErrorResponse',
    'NotFoundResponse',
    'NotImplementedResponse',
    'ORJSONResponse',
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


class ORJSONResponse(JSONResponse):
    """ The response that encodes data into JSON
    """
    def __init__(self, content, default=None, **kwargs):
        self.default = default if default is not None else ORJSONResponse.default_cast
        super().__init__(content, **kwargs)

    def render(self, content: typing.Any) -> bytes:
        return orjson.dumps(content,
            option=orjson.OPT_NON_STR_KEYS,
            default=self.default)

    @staticmethod
    def default_cast(typ):
        """ Cast the data in JSON-serializable type
        """
        str_types = {
            decimal.Decimal
        }
        list_types = {
            set
        }

        if type(typ) in str_types:
            return str(typ)
        if type(typ) in list_types:
            return list(typ)

        raise TypeError(f'Type {type(typ)} is not handled by ORJSONResponse')


class HJSONResponse(ORJSONResponse):
    """ The response that encodes generator data into JSON
    """
    def render(self, content: typing.Generator):
        return super().render(list(content))
