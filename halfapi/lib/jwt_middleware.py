"""
JWT Middleware module

Classes:
    - JWTUser : goes in request.user
    - JWTAuthenticationBackend
    - JWTWebSocketAuthenticationBackend

Raises:
    Exception: If configuration has no SECRET
"""

from os import environ
import typing
from uuid import UUID

from http.cookies import SimpleCookie
import jwt
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, BaseUser, AuthCredentials,
    UnauthenticatedUser)
from starlette.requests import HTTPConnection, Request
from starlette.exceptions import HTTPException

from .user import CheckUser, JWTUser, Nobody
from ..logging import logger
from ..conf import CONFIG
from ..lib.responses import ORJSONResponse

SECRET=None

try:
    with open(CONFIG.get('secret', ''), 'r') as secret_file:
        SECRET = secret_file.read().strip()
except FileNotFoundError:
        logger.error('Could not import SECRET variable from conf module,'\
            ' using HALFAPI_SECRET environment variable')

def cookies_from_scope(scope):
    cookie = dict(scope.get("headers") or {}).get(b"cookie")
    if not cookie:
        return {}

    simple_cookie = SimpleCookie()
    simple_cookie.load(cookie.decode("utf8"))
    return {key: morsel.value for key, morsel in simple_cookie.items()}

def on_auth_error(request: Request, exc: Exception):
    response = ORJSONResponse({"error": str(exc)}, status_code=401)
    response.delete_cookie('Authorization')
    return response

class JWTAuthenticationBackend(AuthenticationBackend):
    def __init__(self, secret_key: str = SECRET,
        algorithm: str = 'HS256', prefix: str = 'JWT'):

        if secret_key is None:
            raise Exception('Missing secret_key argument for JWTAuthenticationBackend')
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.prefix = prefix

    @property
    def id(self) -> str:
        return self.__id

    async def authenticate(
        self, conn: HTTPConnection
    ) -> typing.Optional[typing.Tuple['AuthCredentials', 'BaseUser']]:

        # Standard way to authenticate via API
        # https://datatracker.ietf.org/doc/html/rfc7235#section-4.2
        token = conn.headers.get('Authorization')

        if not token:
            token = cookies_from_scope(conn.scope).get('Authorization')

        is_check_call = 'check' in conn.query_params

        PRODUCTION = conn.scope['app'].debug == False

        if not token and not is_check_call:
            return AuthCredentials(), Nobody()

        try:
            if token:
                payload = jwt.decode(token,
                    key=self.secret_key,
                    algorithms=[self.algorithm],
                    options={
                        'verify_signature': True
                    })

            if is_check_call:
                if token:
                    return AuthCredentials(), CheckUser(payload['user_id'])

                return AuthCredentials(), Nobody()


            if PRODUCTION and 'debug' in payload.keys() and payload['debug']:
                raise AuthenticationError(
                    'Trying to connect using *DEBUG* token in *PRODUCTION* mode')

        except jwt.ExpiredSignatureError as exc:
            return AuthCredentials(), Nobody()
        except jwt.InvalidTokenError as exc:
            raise AuthenticationError(str(exc)) from exc
        except Exception as exc:
            logger.error('Authentication error : %s', exc)
            raise exc


        return AuthCredentials(["authenticated"]), JWTUser(
            user_id=payload['user_id'], token=token, payload=payload)



class JWTWebSocketAuthenticationBackend(AuthenticationBackend):

    def __init__(self, secret_key: str, algorithm: str = 'HS256', query_param_name: str = 'jwt',
                 user_id: UUID = None, audience = None):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.query_param_name = query_param_name
        self.__id = user_id
        self.audience = audience


    async def authenticate(
        self, conn: HTTPConnection
    ) -> typing.Optional[typing.Tuple["AuthCredentials", "BaseUser"]]:

        if self.query_param_name not in conn.query_params:
            return AuthCredentials(), Nobody()

        token = conn.query_params[self.query_param_name]

        try:
            payload = jwt.decode(
                token,
                key=self.secret_key,
                algorithms=[self.algorithm],
                audience=self.audience,
                options={
                    'verify_signature': bool(PRODUCTION)
                })

            if PRODUCTION and 'debug' in payload.keys() and payload['debug']:
                raise AuthenticationError(
                    'Trying to connect using *DEBUG* token in *PRODUCTION* mode')

        except jwt.InvalidTokenError as exc:
            raise AuthenticationError(str(exc)) from exc

        return (
            AuthCredentials(["authenticated"]),
            JWTUser(
                user_id=payload['id'],
                token=token,
                payload=payload)
        )
