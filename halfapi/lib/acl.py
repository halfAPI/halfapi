#!/usr/bin/env python3
"""
Base ACL module that contains generic functions for domains ACL
"""
from dataclasses import dataclass
from functools import wraps
from json import JSONDecodeError
import yaml
from starlette.authentication import UnauthenticatedUser
from starlette.exceptions import HTTPException
from starlette.routing import Route
from starlette.responses import Response

from ..logging import logger

def public(*args, **kwargs) -> bool:
    "Unlimited access"
    return True

def private(*args, **kwargs) -> bool:
    "Forbidden access"
    return False


def connected(fct=public):
    """ Decorator that checks if the user object of the request has been set
    """
    @wraps(fct)
    def caller(req, *args, **kwargs):
        if (not hasattr(req, 'user')
          or isinstance(req.user, UnauthenticatedUser)
          or not hasattr(req.user, 'is_authenticated')):
            return False

        if hasattr(req, 'path_params'):
            return fct(req, **{**kwargs, **req.path_params})
        return fct(req, **{**kwargs})

    return caller

def args_check(fct):
    """ Decorator that puts required and optional arguments in scope

    For GET requests it uses the query_params

    For POST requests it uses the body as JSON

    If "check" is present in the query params, nothing is done.

    If some required arguments are missing, a 400 status code is sent.
    """
    @wraps(fct)
    async def caller(req, *args, **kwargs):
        if 'check' in req.query_params:
            # Check query param should not read the "args"
            return await fct(req, *args, **kwargs)

        data_ = {}
        if req.method == 'GET':
            data_ = dict(req.query_params)

        elif req.method in ['POST', 'PATCH', 'PUT', 'DELETE']:
            if req.scope.get('headers'):
                if b'content-type' not in dict(req.scope.get('headers')):
                    data_ = {}
                else:
                    content_type = dict(req.scope.get('headers')).get(b'content-type').decode().split(';')[0]

                    if content_type == 'application/json':
                        try:
                            data_ = await req.json()
                        except JSONDecodeError as exc:
                            logger.debug('Posted data was not JSON')
                            pass
                    elif content_type in [
                        'multipart/form-data', 'application/x-www-form-urlencoded']:
                        data_ = dict(await req.form())
                    else:
                        data_ = await req.body()

        def plural(array: list) -> str:
            return 's' if len(array) > 1 else ''
        def comma_list(array: list) -> str:
            return ', '.join(array)


        args_d = req.scope.get('args')
        if args_d is not None and isinstance(data_, dict):
            required = args_d.get('required', set())

            missing = []
            data = {}

            for key in required:
                data[key] = data_.get(key, None)
                if data[key] is None:
                    missing.append(key)

            if missing:
                raise HTTPException(
                    400,
                    f"Missing value{plural(missing)} for: {comma_list(missing)}!")

            optional = args_d.get('optional', set())
            for key in optional:
                    if key in data_:
                        data[key] = data_[key]
        else:
            """ Unsafe mode, without specified arguments, or plain text mode
            """
            data = data_

        kwargs['data'] = data

        out_s = req.scope.get('out')
        if out_s:
            kwargs['out'] = list(out_s)

        return await fct(req, *args, **kwargs)

    return caller

# ACLS list for doc and priorities
# Write your own constant in your domain or import this one
# Format : (acl_name: str, acl_documentation: str, priority: int, [public=False])
#
# The 'priority' integer is greater than zero and the lower values means more
# priority. For a route, the order of declaration of the ACLs should respect
# their priority.
#
# When the 'public' boolean value is True, a route protected by this ACL is
# defined on the "/halfapi/acls/acl_name", that returns an empty response and
# the status code 200 or 401.
 
ACLS = (
    ('private', private.__doc__, 0, True),
    ('public', public.__doc__, 999, True)
)

@dataclass
class ACL():
    name: str
    documentation: str
    priority: int
    public: bool = False


class AclRoute(Route):
    def __init__(self, path, acl_fct, acl: ACL):
        self.acl_fct = acl_fct
        self.name = acl.name
        self.description = acl.documentation

        self.docstring = yaml.dump({
            'description': f'{self.name}: {self.description}',
            'responses': {
                '200': {
                    'description': 'ACL OK'
                },
                '401': {
                    'description': 'ACL FAIL'
                }
            }
        })

        async def endpoint(request, *args, **kwargs):
            if request.method == 'GET':
                logger.warning('Deprecated since 0.6.28, use HEAD method since now')

            if self.acl_fct(request, *args, **kwargs) is True:
                return Response(status_code=200)

            return Response(status_code=401)

        endpoint.__doc__ = self.docstring

        return super().__init__(path, methods=['HEAD', 'GET'], endpoint=endpoint)

