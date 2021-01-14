#!/usr/bin/env python3
# builtins
import decimal
import typing as typ
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
    def __init__(self, content, default=None, **kwargs):
        self.default = default if default is not None else ORJSONResponse.default_cast
        super().__init__(content, **kwargs)

    def render(self, content: typ.Any) -> bytes:
        return orjson.dumps(content,
            option=orjson.OPT_NON_STR_KEYS,
            default=self.default)

    @staticmethod
    def default_cast(x):
        types = {
            decimal.Decimal
        }

        if type(x) not in types:
            raise TypeError('Type is not handled in ORJSONResponse')

        return str(x)


class HJSONResponse(ORJSONResponse):
    def render(self, content: typ.Generator):
        return super().render(list(content))
