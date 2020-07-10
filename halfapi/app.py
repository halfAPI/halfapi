#!/usr/bin/env python3
# builtins
import importlib
import sys
from os import environ

# asgi framework
from starlette.applications import Starlette
from starlette.authentication import UnauthenticatedUser
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route
from starlette.types import ASGIApp
from starlette.middleware.authentication import AuthenticationMiddleware

# typing
from typing import Any, Awaitable, Callable, MutableMapping
RequestResponseEndpoint = Callable[ [Request], Awaitable[Response] ]

# hop-generated classes
from .models.api.domain import Domain

# module libraries
from .config import CONFIG
from .lib.jwt_middleware import JWTAuthenticationBackend
from .lib.acl_caller_middleware import AclCallerMiddleware

from .lib.responses import *


def mount_domains(app: ASGIApp, domains: list):
    """ Procedure to mount the registered domains on their prefixes

        Parameters:

            - app (ASGIApp): The Starlette instance
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
            # @TODO 4-configuration
            # Store domain-specific information in a configuration file

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
        # /openapi.json (@TODO : report the bug to FastAPI)
        domain_app.openapi_url = '/api/{version}/{name}/openapi.json'.format(**domain)

        # Mount the domain app on the prefix
        # e.g. : /v4/organigramme
        try:
           app.mount('/{version}/{name}'.format(**domain), app=domain_app)
        except Exception as e:
           print(f'Failed to mount *{domain}*\n')


def startup():
    # This function is called at the instanciation of *app*
    global app

    # Mount the registered domains
    try:
        domains_list = [elt for elt in Domain().select()]
        mount_domains(app, domains_list)
    except Exception as e:
        sys.stderr.write('Error in the *domains* retrieval\n') 
        raise e

if not CONFIG['HALFORM_SECRET']:
    try:
        CONFIG['HALFORM_SECRET'] = open('/etc/half_orm/secret').read()
        print('Missing HALFORM_SECRET variable from configuration, \
            read it from /etc/half_orm/secret')
    except FileNotFoundError:
        print('No HALFORM_SECRET variable set, and /etc/half_orm/secret \
            inaccessible.')
        sys.exit(1)
    except PermissionError:
        print("You don't have the right to read /etc/half_orm/secret")
        sys.exit(1)


debug_routes = [
    Route('/', lambda request, *args, **kwargs: PlainTextResponse('It Works!')),
    Route('/user', lambda request, *args, **kwargs:
        JSONResponse({'user':request.user.json})
        if type(request.user) != UnauthenticatedUser
        else JSONResponse({'user':False})),
    Route('/payload', lambda request, *args, **kwargs:
        JSONResponse({'payload':str(request.payload)}))
] if CONFIG['DEBUG'] else []


app = Starlette(
    debug=CONFIG['DEBUG'],
    routes=debug_routes,
    middleware=[
        Middleware(AuthenticationMiddleware,
            backend=JWTAuthenticationBackend(secret_key=CONFIG['HALFORM_SECRET'])),
        Middleware(AclCallerMiddleware),
    ],
    exception_handlers={
        401: UnauthorizedResponse,
        404: NotFoundResponse,
        500: InternalServerErrorResponse,
        501: NotImplementedResponse
    },
    on_startup=[startup],
)
