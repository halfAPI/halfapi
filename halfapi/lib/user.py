from uuid import UUID
from starlette.authentication import BaseUser, UnauthenticatedUser

class Nobody(UnauthenticatedUser):
    """ Nobody class

    The default class when no token is passed
    """
    @property
    def json(self):
       return {
        'id' : '',
        'token': '',
        'payload': ''
    }


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




