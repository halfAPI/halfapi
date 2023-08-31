import importlib
import inspect
import os
import re

from packaging.specifiers import SpecifierSet
from packaging.version import Version
from typing import Coroutine, Dict, Iterator, List, Tuple
from types import ModuleType, FunctionType

from schema import SchemaError

from starlette.applications import Starlette
from starlette.routing import Router, Route
from starlette.schemas import SchemaGenerator
from .lib.responses import ORJSONResponse

from .lib.acl import AclRoute

import yaml


from . import __version__
from .lib.constants import API_SCHEMA_DICT, ROUTER_SCHEMA, VERBS
from .half_route import HalfRoute
from .lib import acl as lib_acl
from .lib.responses import PlainTextResponse
from .lib.routes import JSONRoute
from .lib.schemas import param_docstring_default
from .lib.domain import MissingAclError, PathError, UnknownPathParameterType, \
    UndefinedRoute, UndefinedFunction, get_fct_name, route_decorator
from .lib.domain_middleware import DomainMiddleware
from .logging import logger

class HalfDomain(Starlette):
    def __init__(self, domain, module=None, router=None, acl=None, app=None):
        """
        Parameters:
            domain (str): Module name (should be importable)
            router (str): Router name (should be importable from domain module
                defaults to __router__ variable from domain module)
            app (HalfAPI): The app instance
        """
        self.app = app

        self.m_domain = importlib.import_module(domain) if module is None else module
        self.d_domain = getattr(self.m_domain, 'domain', domain)
        self.name = self.d_domain['name']
        self.id = self.d_domain['id']
        self.version = self.d_domain['version']
        self.halfapi_version = self.d_domain.get('halfapi_version', __version__)
        self.deps = self.d_domain.get('deps', tuple())
        self.schema_components = self.d_domain.get('schema_components', dict())

        if not router:
            self.router = self.d_domain.get('routers', '.routers')
        else:
            self.router = router

        self.m_router = None
        try:
            self.m_router = importlib.import_module(self.router, self.m_domain.__package__)
        except AttributeError:
            raise Exception('no router module')

        self.m_acl = HalfDomain.m_acl(self.m_domain, acl)

        self.config = { **app.config }

        logger.info('HalfDomain creation %s %s', domain, self.config)

        for elt in self.deps:
            package, version = elt
            specifier = SpecifierSet(version)
            package_module = importlib.import_module(package)
            if Version(package_module.__version__) not in specifier:
                raise Exception(
                    'Wrong version for package {} version {} (excepting {})'.format(
                        package, package_module.__version__, specifier
                    ))


        super().__init__(
            routes=self.gen_domain_routes(),
            middleware=[
                (DomainMiddleware, {
                    'domain': {
                        'name': self.name,
                        'id': self.id,
                        'version': self.version,
                        'halfapi_version': self.halfapi_version,
                        'config': self.config.get('domain', {}).get(self.name, {}).get('config', {})
                    }
                })
            ]
        )

    @staticmethod
    def name(module):
        """ Returns the name declared in the 'domain' dict at the root of the package
        """
        return module.domain['name']
        

    @staticmethod
    def m_acl(module, acl=None):
        """ Returns the imported acl module for the domain module
        """
        if not acl:
            acl = getattr(module, '__acl__', '.acl')

        return importlib.import_module(acl, module.__package__)


    @staticmethod
    def acls(module, acl=None):
        """ Returns the ACLS constant for the given domain
        """
        m_acl = HalfDomain.m_acl(module, acl)
        try:
            return [
                lib_acl.ACL(*elt)
                for elt in getattr(m_acl, 'ACLS')
            ]
        except AttributeError as exc:
            logger.error(exc)
            raise Exception(
                f'Missing acl.ACLS constant in module {m_acl.__package__}') from exc

    @staticmethod
    def acls_route(domain, module_path=None, acl=None):
        """ Dictionary of acls

        Format :

        {
            [acl_name]: {
                callable: fct_reference,
                docs: fct_docstring,
            }
        }
        """

        d_res = {}

        module = importlib.import_module(domain) \
            if module_path is None \
            else importlib.import_module(module_path)

        m_acl = HalfDomain.m_acl(module, acl)

        for elt in HalfDomain.acls(module, acl=acl):

            fct = getattr(m_acl, elt.name)

            d_res[elt.name] = {
                'callable': fct,
                'docs': elt.documentation
            }

        return d_res

    @staticmethod
    def acls_router(domain, module_path=None, acl=None):
        """ Returns a Router object with the following routes :

        / : The "acls" field of the API metadatas
        /{acl_name} : If the ACL is defined as public, a route that returns either status code 200 or 401 on HEAD/GET request
        """

        routes = []
        d_res = {}

        module = importlib.import_module(domain) \
            if module_path is None \
            else importlib.import_module(module_path)


        m_acl = HalfDomain.m_acl(module, acl)

        for elt in HalfDomain.acls(module, acl=acl):

            fct = getattr(m_acl, elt.name)

            d_res[elt.name] = {
                'callable': fct,
                'docs': elt.documentation,
                'public': elt.public
            }

            if elt.public:
                try:
                    if inspect.iscoroutinefunction(fct):
                        logger.warning('async decorator are not yet supported')
                    else:
                        inner = fct()

                        if inspect.iscoroutinefunction(fct) or callable(inner):
                            fct = inner

                except TypeError:
                    # Fct is not a decorator or is not well called (has no default arguments)
                    # We can ignore this
                    pass

                routes.append(
                    AclRoute(f'/{elt.name}', fct, elt)
                )

        d_res_under_domain_name = {}
        d_res_under_domain_name[HalfDomain.name(module)] = d_res

        routes.append(
            Route(
                '/',
                JSONRoute(d_res_under_domain_name),
                methods=['GET']
            )
        )

        return Router(routes)


    @staticmethod
    def gen_routes(m_router: ModuleType,
        verb: str,
        path: List[str],
        params: List[Dict],
        path_param_docstrings: Dict[str, str] = {}) -> Tuple[FunctionType, Dict]:
        """
        Returns a tuple of the function associatied to the verb and path arguments,
        and the dictionary of it's acls

        Parameters:
            - m_router (ModuleType): The module containing the function definition

            - verb (str): The HTTP verb for the route (GET, POST, ...)

            - path (List): The route path, as a list (each item being a level of
                deepness), from the lowest level (domain) to the highest

            - params (Dict): The acl list of the following format :
                [{'acl': Function, 'args': {'required': [], 'optional': []}}]


        Returns:

            (Function, Dict): The destination function and the acl dictionary

        """
        if len(params) == 0:
            raise MissingAclError('[{}] {}'.format(verb, '/'.join(path)))

        if len(path) == 0:
            logger.error('Empty path for [{%s}]', verb)
            raise PathError()

        fct_name = get_fct_name(verb, path[-1])
        if hasattr(m_router, fct_name):
            fct = getattr(m_router, fct_name)
            fct_docstring_obj = yaml.safe_load(fct.__doc__)
            if 'parameters' not in fct_docstring_obj and path_param_docstrings:
                fct_docstring_obj['parameters'] = list(map(
                    yaml.safe_load,
                    path_param_docstrings.values()))

            fct.__doc__ = yaml.dump(fct_docstring_obj)
        else:
            raise UndefinedFunction('{}.{}'.format(m_router.__name__, fct_name or ''))


        if not inspect.iscoroutinefunction(fct):
            return route_decorator(fct), params

        # TODO: Remove when using only sync functions
        return lib_acl.args_check(fct), params


    @staticmethod
    def gen_router_routes(m_router, path: List[str], PATH_PARAMS={}) -> \
        Iterator[Tuple[str, str, ModuleType, Coroutine, List]]:
        """
        Recursive generator that parses a router (or a subrouter)
        and yields from gen_routes

        Parameters:

            - m_router (ModuleType): The currently treated router module
            - path (List[str]): The current path stack

        Yields:

            (str, str, ModuleType, Coroutine, List): A tuple containing the path, verb,
                router module, function reference and parameters of the route.
                Function and parameters are yielded from then gen_routes function,
                that decorates the endpoint function.
        """

        for subpath, params in HalfDomain.read_router(m_router).items():
            path.append(subpath)

            for verb in VERBS:
                if verb not in params:
                    continue
                yield ('/'.join(filter(lambda x: len(x) > 0, path)),
                    verb,
                    m_router,
                    *HalfDomain.gen_routes(m_router, verb, path, params[verb], PATH_PARAMS)
                )

            for subroute in params.get('SUBROUTES', []):
                subroute_module = importlib.import_module(f'.{subroute}', m_router.__name__)
                param_match = re.fullmatch('^([A-Z_]+)_([a-z]+)$', subroute)
                parameter_name = None
                if param_match is not None:
                    try:
                        parameter_name = param_match.groups()[0].lower()
                        if parameter_name in PATH_PARAMS:
                            raise Exception(f'Duplicate parameter name in same path! {subroute} : {parameter_name}')

                        parameter_type = param_match.groups()[1]
                        path.append('{{{}:{}}}'.format(
                            parameter_name,
                            parameter_type,
                            )
                        )


                        try:
                            PATH_PARAMS[parameter_name] = subroute_module.param_docstring
                        except AttributeError as exc:
                            PATH_PARAMS[parameter_name] = param_docstring_default(parameter_name, parameter_type)

                    except AssertionError as exc:
                        raise UnknownPathParameterType(subroute) from exc
                else:
                    path.append(subroute)

                try:
                    yield from HalfDomain.gen_router_routes(
                        subroute_module,
                        path,
                        PATH_PARAMS
                    )

                except ImportError as exc:
                    logger.error('Failed to import subroute **{%s}**', subroute)
                    raise exc

                path.pop()
                if parameter_name:
                    PATH_PARAMS.pop(parameter_name)


            path.pop()


    @staticmethod
    def read_router(m_router: ModuleType) -> Dict:
        """
        Reads a module and returns a router dict

        If the module has a "ROUTES" constant, it just returns this constant,
        Else, if the module has an "ACLS" constant, it builds the accurate dict

        TODO: May be another thing, may be not a part of halfAPI

        """
        m_path = None

        try:
            if not hasattr(m_router, 'ROUTES'):
                routes = {'':{}}
                acls = getattr(m_router, 'ACLS') if hasattr(m_router, 'ACLS') else None

                if acls is not None:
                    for method in acls.keys():
                        if method not in VERBS:
                            raise Exception(
                                'This method is not handled: {}'.format(method))

                        routes[''][method] = []
                        routes[''][method] = acls[method].copy()

                routes['']['SUBROUTES'] = []
                if hasattr(m_router, '__path__'):
                    """ Module is a package
                    """
                    m_path = getattr(m_router, '__path__')
                    if isinstance(m_path, list) and len(m_path) == 1:
                        routes['']['SUBROUTES'] = [
                            elt.name
                            for elt in os.scandir(m_path[0])
                            if elt.is_dir()
                        ]
            else:
                routes = getattr(m_router, 'ROUTES')

            try:
                ROUTER_SCHEMA.validate(routes)
            except SchemaError as exc:
                logger.error(routes)
                raise exc

            return routes
        except ImportError as exc:
            # TODO: Proper exception handling
            raise exc
        except FileNotFoundError as exc:
            # TODO: Proper exception handling
            logger.error(m_path)
            raise exc

    def gen_domain_routes(self):
        """
        Yields the Route objects for a domain

        Parameters:
            m_domains: ModuleType

        Returns:
            Generator(HalfRoute)
        """
        yield HalfRoute('/',
            self.schema_openapi(),
            [{'acl': lib_acl.public}],
            'GET'
        )

        for path, method, m_router, fct, params in HalfDomain.gen_router_routes(self.m_router, []):
            yield HalfRoute(f'/{path}', fct, params, method)

    def schema_dict(self) -> Dict:
        """ gen_router_routes return values as a dict
        Parameters:

        m_router (ModuleType): The domain routers' module

        Returns:

        Dict: Schema of dict is halfapi.lib.constants.DOMAIN_SCHEMA

        @TODO: Should be a "router_schema_dict" function
        """
        d_res = {}

        for path, verb, m_router, fct, parameters in HalfDomain.gen_router_routes(self.m_router, []):
            if path not in d_res:
                d_res[path] = {}

            if verb not in d_res[path]:
                d_res[path][verb] = {}

            d_res[path][verb]['callable'] = f'{m_router.__name__}:{fct.__name__}'
            try:
                d_res[path][verb]['docs'] = yaml.safe_load(fct.__doc__)
            except AttributeError:
                logger.error(
                    'Cannot read docstring from fct (fct=%s path=%s verb=%s', fct.__name__, path, verb)

            d_res[path][verb]['acls'] = list(map(lambda elt: { **elt, 'acl': elt['acl'].__name__ },
                parameters))

        return d_res


    def schema(self) -> Dict:
        schema = { **API_SCHEMA_DICT }
        schema['domain'] = {
            'name': self.name,
            'id': self.id,
            'version': getattr(self.m_domain, '__version__', ''),
            'patch_release': getattr(self.m_domain, '__patch_release__', ''),
            'routers': self.m_router.__name__,
            'acls': tuple(getattr(self.m_acl, 'ACLS', ()))
        }
        schema['paths'] = self.schema_dict()
        return schema

    def schema_openapi(self) -> Route:
        schema = SchemaGenerator(
            {
                'openapi': '3.0.0',
                'info': {
                    'title': self.name,
                    'version': self.version,
                    'x-acls': tuple(getattr(self.m_acl, 'ACLS', ())),
                    **({
                      f'x-{key}': value
                      for key, value in self.d_domain.items()
                    }),
                },
                'components': self.schema_components
            }

        )

        async def inner(request, *args, **kwargs):
            """
            description: |
              Returns the current API routes description (OpenAPI v3)
              as a JSON object
            responses:
              200:
                description: API Schema in OpenAPI v3 format
            """
            return ORJSONResponse(
                schema.get_schema(routes=request.app.routes))

        return inner

