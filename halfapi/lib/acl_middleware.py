#!/usr/bin/env python3
from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class AclMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, acl_module):
        super().__init__(app)
        self.acl_module = acl_module
    async def dispatch(self, request: Request, call_next):
        """ Checks the "acls" key in the scope and applies the
            corresponding functions in the current module's acl lib.

            Raises an exception if no acl function returns True
        """
        print(f'Hit acl {__name__} middleware')

        if 'dev_route' in request.scope.keys():
            print('[DEBUG] Dev route, no ACL')
            return await call_next(request)

        if not('acls' in request.scope.keys()
            and type(request.scope['acls']) == list):

            print('BUG : scope["acls"] does not exist or is not a list')
            raise HTTPException(500)

        for acl_fct_name in request.scope['acls']:
            print(f'Will apply {acl_fct_name}')
            try:
                fct = getattr(self.acl_module, acl_fct_name)
                if fct(request) is True:
                    return await call_next(request)

            except AttributeError as e:
                print(f'No ACL function "{acl_fct_name}" in {__name__} module')
                print(e)
                break

            except Exception as e:
                print(e)
                raise HTTPException(500)

        raise HTTPException(401)
