__LICENSE__ = """
BSD 3-Clause License

Copyright (c) 2018, Amit Ripshtos
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import jwt
from uuid import UUID
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, BaseUser, AuthCredentials,
    UnauthenticatedUser)


class JWTUser(BaseUser):
    def __init__(self, id: UUID, token: str, payload: dict) -> None:
        self.__id = id
        self.token = token
        self.payload = payload

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def id(self) -> str:
        return self.id


class JWTAuthenticationBackend(AuthenticationBackend):

    def __init__(self, secret_key: str, algorithm: str = 'HS256', prefix: str = 'JWT', name: str = 'name'):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.prefix = prefix
        self.id = id

    async def authenticate(self, request):
        if "Authorization" not in request.headers:
            return None

        token = request.headers["Authorization"]
        try:
            payload = jwt.decode(token, key=self.secret_key, algorithms=self.algorithm)
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(str(e))

        return AuthCredentials(["authenticated"]), JWTUser(
            id=payload['id'], token=token, payload=payload)


class JWTWebSocketAuthenticationBackend(AuthenticationBackend):

    def __init__(self, secret_key: str, algorithm: str = 'HS256', query_param_name: str = 'jwt',
                 id: UUID = None, audience = None, options = {}):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.query_param_name = query_param_name
        self.id = id
        self.audience = audience
        self.options = options


    async def authenticate(self, request):
        if self.query_param_name not in request.query_params:
            return AuthCredentials(), UnauthenticatedUser()

        token = request.query_params[self.query_param_name]

        try:
            payload = jwt.decode(token, key=self.secret_key, algorithms=self.algorithm,
                                 audience=self.audience, options=self.options)
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(str(e))

        return AuthCredentials(["authenticated"]), JWTUser(id = payload['id'],
                                                           token=token, payload=payload)
