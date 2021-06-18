#!/usr/bin/env python3
"""
Base ACL module that contains generic functions for domains ACL
"""
import logging
from functools import wraps
from json import JSONDecodeError
from starlette.authentication import UnauthenticatedUser
from starlette.exceptions import HTTPException


logger = logging.getLogger('uvicorn.asgi')

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

        return fct(req, **{**kwargs, **req.path_params})

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

        if req.method == 'GET':
            data_ = req.query_params

        if req.method == 'POST':
            try:
                data_ = await req.json()
            except JSONDecodeError as exc:
                data_ = {}

        def plural(array: list) -> str:
            return 's' if len(array) > 1 else ''
        def comma_list(array: list) -> str:
            return ', '.join(array)


        args_d = kwargs.get('args', None)
        if args_d is not None:
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
            """ Unsafe mode, without specified arguments
            """
            data = data_

        kwargs['data'] = data

        return await fct(req, *args, **kwargs)

    return caller
