#!/usr/bin/env python3
from starlette.requests import Request
from starlette.exceptions import HTTPException

@app.middleware('http')
async def acl_middleware(request: Request, call_next):
    """ Checks the "acls" key in the scope and applies the
        corresponding functions in the current module's acl lib.

        Raises an exception if no acl function returns True
    """
    print(f'Hit acl {__name__} middleware')

    for acl_fnct_name in request.scope['acls']:
        print(f'Will apply {acl_fnct_name}')
        try:
            fct = getattr(acl, acl_fct_name)
            if fct(request) is True:
                print(f'{fct} : {fct(request)}\n')

                return await call_next(request)

        except AttributeError as e:
            print(f'No ACL function "{acl_fct_name}" in {__name__} module')
            print(e)
            break

        except Exception as e:
            print(e)
            raise HTTPException(500)

    raise HTTPException(401)
