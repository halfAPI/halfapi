#!/usr/bin/env python3
# builtins
import importlib
import sys
from os import environ

# asgi framework
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route, Match, Mount
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.middleware.authentication import AuthenticationMiddleware

# typing
from typing import Any, Awaitable, Callable, MutableMapping
RequestResponseEndpoint = Callable[ [Request], Awaitable[Response] ]

# hop-generated classes
from .models.api.acl_function import AclFunction
from .models.api.domain import Domain
from .models.api.route import Route
from .models.api.view.acl import Acl as AclView
from .models.api.view.route import Route as RouteView

# module libraries
from .lib.responses import ForbiddenResponse, NotFoundResponse
from .lib.jwt_middleware import JWTAuthenticationBackend

def match_route(app: ASGIApp, scope: Scope):
    """ Checks all routes from "app" and checks if it matches with the one from
        scope

        Parameters:

            - app (ASGIApp): The Starlette object
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
    result = {
        'domain': None,
        'name': None,
        'http_verb': None,
        'version': None
    }

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


        if scope['path'].split('/')[-1] not in ['docs','openapi.json','redoc']:
            # routes in the the database, the others being
            # docs/openapi.json/redoc
            try:
                d_match, path_params = match_route(app, scope)
            except HTTPException:
                return NotFoundResponse()
            except Exception as e:
                raise e

            d_match, path_params = match_route(app, scope)

            try:
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

        return await self.app(scope, receive, send)


def mount_domains(app: Starlette, domains: list):
    """ Procedure to mount the registered domains on their prefixes

        Parameters:

            - app (FastAPI): The FastAPI object
            - domains (list): The domains to mount, retrieved from the database
              with their attributes "version", "name"

        Returns: Nothing
    """

    for domain in domains:
        if 'name' not in domain.keys() or 'version' not in domain.keys():
            continue

        # Retrieve domain app according to domain details
        try:
            print(f'Will import {domain["name"]}.app:app')
            #@TODO let the configuration come from the domain module - (or apidb)
            environ["HALFORM_DSN"] = "dbname=si user=si"
            domain_mod = importlib.import_module(
                f'{domain["name"]}.app')
            domain_app = domain_mod.app
        except ModuleNotFoundError:
            sys.stderr.write(
                f'Could not find module *{domain["name"]}* in sys.path\n')
            continue
        except ImportError:
            sys.stderr.write(f'Could not import *app* from *{domain}*')
            continue
        except Exception as e:
            sys.stderr.write(f'Error in import *{domain["name"]}*\n')
            print(e)
            continue


        # Alter the openapi_url so the /docs page doesn't try to get
        # /{name}/openapi.json (@TODO : retport the bug to FastAPI)
        # domain_app.openapi_url = '/../api/{version}/{name}/openapi.json'.format(**domain)

        # Mount the domain app on the prefix
        # e.g. : /v4/organigramme
        try:
           app.mount('/{version}/{name}'.format(**domain), app=domain_app)
        except Exception as e:
           print(f'Failed to mount *{domain}*\n')


def startup():
    global app
    # Mount the registered domains
    try:
        domains_list = [elt for elt in Domain().select()]
        mount_domains(app, domains_list)
    except Exception as e:
        sys.stderr.write('Error in the *domains* retrieval\n') 
        raise e

async def root(request):
    return JSONResponse({'payload': request.payload})

def check_conf():
    if not environ.get('HALFORM_SECRET', False):
        environ['HALFORM_SECRET'] = 'secret'
        print('Missing HALFORM_SECRET variable from configuration, seting to default')

    if not environ.get('HALFORM_DSN', False):
        print('Missing HALFORM_DSN variable from configuration')

app = Starlette(
    middleware=[
        Middleware(AuthenticationMiddleware, backend=JWTAuthenticationBackend(secret_key=environ.get('HALFORM_SECRET'))),
        Middleware(AclCallerMiddleware),
    ],
    on_startup=[startup],
)
