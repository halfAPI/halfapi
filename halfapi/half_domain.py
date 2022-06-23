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
from starlette.routing import Router

import yaml


from . import __version__
from .lib.constants import API_SCHEMA_DICT, ROUTER_SCHEMA, VERBS
from .half_route import HalfRoute
from .lib import acl
from .lib.routes import JSONRoute
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
        self.name = getattr(self.m_domain, '__name__', domain)
        self.id = getattr(self.m_domain, '__id__')
        self.version = getattr(self.m_domain, '__version__', '0.0.0')
        # TODO: Check if given domain halfapi_version matches with __version__
        self.halfapi_version = getattr(self.m_domain, '__halfapi_version__', __version__)

        self.deps = getattr(self.m_domain, '__deps__', tuple())

        if not router:
            self.router = getattr(domain, '__router__', '.routers')
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
            return getattr(m_acl, 'ACLS')
        except AttributeError:
            raise Exception(f'Missing acl.ACLS constant in module {m_acl.__package__}')

    @staticmethod
    def acls_route(domain, module_path=None, acl=None):
        """ Dictionary of acls

        Format :

        {
            [acl_name]: {
                callable: fct_reference,
                docs: fct_docstring,
                result: fct_result
            }
        }
        """

        d_res = {}

        module = importlib.import_module(domain) \
            if module_path is None \
            else importlib.import_module(module_path)

        m_acl = HalfDomain.m_acl(module, acl)

        for acl_name, doc, order in HalfDomain.acls(
            module,
            acl=acl):
            fct = getattr(m_acl, acl_name)
            d_res[acl_name] = {
                'callable': fct,
                'docs': doc,
                'result': None
            }
        return d_res

    # def schema(self):

    @staticmethod
    def gen_routes(m_router: ModuleType,
        verb: str,
        path: List[str],
        params: List[Dict]) -> Tuple[FunctionType, Dict]:
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
        else:
            raise UndefinedFunction('{}.{}'.format(m_router.__name__, fct_name or ''))


        if not inspect.iscoroutinefunction(fct):
            return route_decorator(fct), params

        # TODO: Remove when using only sync functions
        return acl.args_check(fct), params


    @staticmethod
    def gen_router_routes(m_router, path: List[str]) -> \
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
                    *HalfDomain.gen_routes(m_router, verb, path, params[verb])
                )

            for subroute in params.get('SUBROUTES', []):
                #logger.debug('Processing subroute **%s** - %s', subroute, m_router.__name__)
                param_match = re.fullmatch('^([A-Z_]+)_([a-z]+)$', subroute)
                if param_match is not None:
                    try:
                        path.append('{{{}:{}}}'.format(
                            param_match.groups()[0].lower(),
                            param_match.groups()[1]))
                    except AssertionError as exc:
                        raise UnknownPathParameterType(subroute) from exc
                else:
                    path.append(subroute)

                try:
                    yield from HalfDomain.gen_router_routes(
                        importlib.import_module(f'.{subroute}', m_router.__name__),
                        path)

                except ImportError as exc:
                    logger.error('Failed to import subroute **{%s}**', subroute)
                    raise exc

                path.pop()

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
            JSONRoute([ self.schema() ]),
            [{'acl': acl.public}],
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
