#!/usr/bin/env python3
from os import environ

from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match, Mount
from starlette.types import ASGIApp, Receive, Scope, Send

from halfapi.models.api.view.acl import Acl as AclView

class DebugRouteException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self)

def match_route(app: ASGIApp, scope: Scope):
    """ Checks all routes from "app" and checks if it matches with the one from
        scope

        Parameters:

            - app (ASGIApp): The Starlette instance
            - scope (MutableMapping[str, Any]): The requests scope

        Returns:

            - (dict, dict): The first dict of the tuple is the details on the
                route, the second one is the path parameters

        Raises:

            HTTPException
    """

    """ The *result* variable is fitted to the filter that will be applied when
        searching the route in the database.
        Refer to the database documentation for more details on the api.route
        table.
    """

    print('3')
    from ..app import CONFIG
    print(CONFIG)

    result = {
        'domain': None,
        'name': None,
        'http_verb': None,
        'version': None
    }

    if 'DEBUG' in CONFIG.keys() and len(scope['path'].split('/')) <= 3:
        raise DebugRouteException()

    try:
        """ Identification of the parts of the path

            Examples :
                version : v4
                domain : organigramme
                path : laboratoire/personnel
        """
        _, result['domain'], path = scope['path'].split('/', 2)
    except ValueError as e:
        #404 Not found
        raise HTTPException(404)
    # Prefix the path with "/"
    path = f'/{path}'

    for route in app.routes:

        if type(route) != Mount:
            """ The root app should not have exposed routes,
                only the mounted domains have some.
            """
            continue

        """ Clone the scope to assign the path to the path without the
            matching domain, be careful to the "root_path" of the mounted domain.

            @TODO
            Also, improper array unpacking may make crash the program without any
            explicit error, we may have to improve this as we only rely on this
            function to accomplish all the routing
        """
        subscope = scope.copy()
        _, result['domain'], subpath = path.split('/', 2)
        subscope['path'] = f'/{subpath}'

        for mount_route in route.routes:
            # Parse all domain routes
            submatch = mount_route.matches(subscope)
            if submatch[0] != Match.FULL:
                continue

            # Route matches
            try:
                result['name'] = submatch[1]['endpoint'].__name__
                result['http_verb'] = scope['method']
            except Exception as e:
                print(e)

            return result, submatch[1]['path_params']

    raise HTTPException(404)


class AclCallerMiddleware(BaseHTTPMiddleware):
    async def __call__(self, scope:Scope, receive: Receive, send: Send) -> None:
        """ Points out to the domain which ACL function it should call

            Parameters :

                - request (Request): The current request

                - call_next (RequestResponseEndpoint): The next middleware/route function

            Return:
                Response
        """
        print('Hit AclCallerMiddleware of API')
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        app = self.app
        while True:
            if not hasattr(app, 'app'):
                break
            app = app.app

        if scope['path'].split('/')[-1] not in ['docs','openapi.json','redoc']:
            # routes in the the database, the others being
            # docs/openapi.json/redoc

            try:
                d_match, path_params = match_route(app, scope)
                scope['acls'] = []
                for acl in AclView(**d_match).select():
                    # retrieve related ACLs

                    if ('acl_function_name' not in acl.keys()
                    or 'domain' not in acl.keys()):
                        continue

                    scope['acls'].append(acl['acl_function_name'])

            except StopIteration:
                # TODO : No ACL sur une route existante, prevenir l'admin?
                print("No ACL")
                pass
            except DebugRouteException:
                print("Debug route")
                if 'DEBUG_ACL' in environ.keys():
                    scope['acls'] = environ['DEBUG_ACL'].split(':')
                else:
                    scope['acls'] = []

        return await self.app(scope, receive, send)
