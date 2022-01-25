""" HalfRoute

Child class of starlette.routing.Route
"""
from functools import partial, wraps

from typing import Callable, Coroutine, List, Dict
from types import FunctionType

from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.exceptions import HTTPException

from .logging import logger
from .lib.domain import MissingAclError, PathError, UnknownPathParameterType, \
    UndefinedRoute, UndefinedFunction

class HalfRoute(Route):
    """ HalfRoute
    """
    def __init__(self, path: List[str], fct: Callable, params: List[Dict], method: str):
        logger.info('HalfRoute creation: %s %s %s %s', path, fct, params, method)
        if len(params) == 0:
            raise MissingAclError('[{}] {}'.format(method, '/'.join(path)))

        if len(path) == 0:
            logger.error('Empty path for [{%s}]', method)
            raise PathError()

        super().__init__(
            path,
            HalfRoute.acl_decorator(
                fct,
                params
            ),
            methods=[method])

    @staticmethod
    def acl_decorator(fct: Callable = None, params: List[Dict] = None) -> Coroutine:
        """
        Decorator for async functions that calls pre-conditions functions
        and appends kwargs to the target function


        Parameters:
            fct (Callable):
                The function to decorate

            params List[Dict]:
                A list of dicts that have an "acl" key that points to a function

        Returns:
            async function
        """

        if not params:
            params = []

        if not fct:
            return partial(HalfRoute.acl_decorator, params=params)


        @wraps(fct)
        async def caller(req: Request, *args, **kwargs):
            for param in params:
                if param.get('acl'):
                    passed = param['acl'](req, *args, **kwargs)
                    if isinstance(passed, FunctionType):
                        passed = param['acl']()(req, *args, **kwargs)

                    if not passed:
                        logger.debug(
                            'ACL FAIL for current route (%s - %s)', fct, param.get('acl'))
                        continue

                    logger.debug(
                        'ACL OK for current route (%s - %s)', fct, param.get('acl'))

                    req.scope['acl_pass'] = param['acl'].__name__

                    if 'args' in param:
                        req.scope['args'] = param['args']
                        logger.debug(
                            'Args for current route (%s)', param.get('args'))

                    if 'out' in param:
                        req.scope['out'] = param['out']

                    if 'out' in param:
                        req.scope['out'] = param['out'].copy()

                    if 'check' in req.query_params:
                        return PlainTextResponse(param['acl'].__name__)

                    logger.debug('acl_decorator %s', param)
                    logger.debug('calling %s:%s %s %s', fct.__module__, fct.__name__, args, kwargs)
                    return await fct(
                        req, *args,
                        **{
                            **kwargs,
                        })

            if 'check' in req.query_params:
                return PlainTextResponse('')

            raise HTTPException(401)

        return caller
