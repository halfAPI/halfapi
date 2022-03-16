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

import jwt
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, BaseUser, AuthCredentials,
    UnauthenticatedUser)
from starlette.requests import HTTPConnection
from starlette.exceptions import HTTPException

from .user import CheckUser, JWTUser, Nobody
from ..logging import logger
from ..conf import CONFIG

SECRET=None

try:
    with open(CONFIG.get('secret', ''), 'r') as secret_file:
        SECRET = secret_file.read().strip()
except FileNotFoundError:
        logger.error('Could not import SECRET variable from conf module,'\
            ' using HALFAPI_SECRET environment variable')

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


        token = conn.headers.get('Authorization')
        is_check_call = 'check' in conn.query_params
        is_fake_user_id = is_check_call and 'user_id' in conn.query_params
        PRODUCTION = conn.scope['app'].debug == False

        if not token and not is_check_call:
            return AuthCredentials(), Nobody()

        try:
            if token and not is_fake_user_id:
                payload = jwt.decode(token,
                    key=self.secret_key,
                    algorithms=[self.algorithm],
                    options={
                        'verify_signature': True
                    })

            if is_check_call:
                if is_fake_user_id:
                    try:
                        fake_user_id = UUID(conn.query_params['user_id'])

                        return AuthCredentials(), CheckUser(fake_user_id)
                    except ValueError as exc:
                        raise HTTPException(400, 'user_id parameter not an uuid')

                if token:
                    return AuthCredentials(), CheckUser(payload['user_id'])

                return AuthCredentials(), Nobody()


            if PRODUCTION and 'debug' in payload.keys() and payload['debug']:
                raise AuthenticationError(
                    'Trying to connect using *DEBUG* token in *PRODUCTION* mode')

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
