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
    - ServiceUnavailableResponse
    - UnauthorizedResponse
    - ODSResponse

"""
from datetime import date
import decimal
import typing
from io import BytesIO
import orjson

# asgi framework
from starlette.responses import PlainTextResponse, Response, JSONResponse

from .user import JWTUser, Nobody


__all__ = [
    'HJSONResponse',
    'InternalServerErrorResponse',
    'NotFoundResponse',
    'NotImplementedResponse',
    'ORJSONResponse',
    'PlainTextResponse',
    'ServiceUnavailableResponse',
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

class ServiceUnavailableResponse(Response):
    """ The 503 Service Unavailable default Response
    """
    def __init__(self, *args, **kwargs):
        super().__init__(status_code=503)

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
        jsonable_types = {
            JWTUser, Nobody
        }

        if callable(typ):
            return typ.__name__
        if type(typ) in str_types:
            return str(typ)
        if type(typ) in list_types:
            return list(typ)
        if type(typ) in jsonable_types:
            return typ.json

        raise TypeError(f'Type {type(typ)} is not handled by ORJSONResponse')


class HJSONResponse(ORJSONResponse):
    """ The response that encodes generator data into JSON
    """
    def render(self, content: typing.Generator):
        return super().render(list(content))

class ODSResponse(Response):
    def __init__(self, d_rows: typing.List[typing.Dict]):
        try:
            import pyexcel as pe
        except ImportError:
            """ ODSResponse is not handled
            """
            super().__init__(content=
                'pyexcel is not installed, ods format not available'
            )
            return

        with BytesIO() as ods_file:
            # rows.insert(0, rownames)
            self.sheet = pe.Sheet(d_rows)
            self.sheet.save_to_memory(
                file_type='ods',
                stream=ods_file)

            filename = f'{date.today()}.ods'

            super().__init__(
                content=ods_file.getvalue(),
                headers={
                    'Content-Type': 'application/vnd.oasis.opendocument.spreadsheet; charset=UTF-8',
                    'Content-Disposition': f'attachment; filename="{filename}"'},
                status_code = 200)

