"""
JWT Middleware module

Classes:
    - JWTUser : goes in request.user
    - JWTAuthenticationBackend
    - JWTWebSocketAuthenticationBackend

Raises:
    Exception: If configuration has no SECRET or HALFAPI_SECRET is not set
"""

from os import environ
import typing
import logging
from uuid import UUID

import jwt
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, BaseUser, AuthCredentials,
    UnauthenticatedUser)
from starlette.requests import HTTPConnection
from starlette.exceptions import HTTPException

logger = logging.getLogger('halfapi')

"""
@OLD : old way to check production setting, we can simply check app's "debug" attribute

try:
    from ..conf import PRODUCTION
except ImportError:
    logger.warning('Could not import PRODUCTION variable from conf module,'\
        ' using HALFAPI_PROD environment variable')
    PRODUCTION = bool(environ.get('HALFAPI_PROD', False))
"""

try:
    from ..conf import SECRET
except ImportError as exc:
    logger.warning('Could not import SECRET variable from conf module,'\
        ' using HALFAPI_SECRET environment variable')
    SECRET  = environ.get('HALFAPI_SECRET', False)
    if not SECRET:
        raise Exception('Missing HALFAPI_SECRET variable') from exc



class JWTUser(BaseUser):
    """ JWTUser class

    Is used to store authentication informations
    """
    def __init__(self, user_id: UUID, token: str, payload: dict) -> None:
        self.__id = user_id
        self.token = token
        self.payload = payload

    def __str__(self):
        return str(self.json)

    @property
    def json(self):
        return {
            'id' : str(self.__id),
            'token': self.token,
            'payload': self.payload
        }

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return ' '.join(
            (self.payload.get('name'), self.payload.get('firstname')))

    @property
    def id(self) -> str:
        return self.__id


class CheckUser(BaseUser):
    """ CheckUser class

    Is used to call checks with give user_id, to know if it passes the ACLs for
    the given route.

    It should never be able to run a route function.
    """
    def __init__(self, user_id: UUID) -> None:
        self.__id = user_id


    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return 'check_user'

    @property
    def id(self) -> str:
        return self.__id



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
            return AuthCredentials(), UnauthenticatedUser()

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
                else:
                    return AuthCredentials(), UnauthenticatedUser()


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
            return AuthCredentials(), UnauthenticatedUser()

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
