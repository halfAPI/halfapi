import importlib
import inspect
import os
import re

from typing import Coroutine, Dict, Iterator, List, Tuple
from types import ModuleType, FunctionType

from schema import SchemaError

from starlette.applications import Starlette
from starlette.routing import Router

import yaml


from .lib.constants import API_SCHEMA_DICT, ROUTER_SCHEMA, VERBS
from .half_route import HalfRoute
from .lib import acl
from .lib.routes import JSONRoute
from .lib.domain import MissingAclError, PathError, UnknownPathParameterType, \
    UndefinedRoute, UndefinedFunction, get_fct_name, route_decorator
from .lib.domain_middleware import DomainMiddleware
from .logging import logger

class HalfDomain(Starlette):
    def __init__(self, app, domain, router=None, config={}):
        self.app = app

        self.m_domain = importlib.import_module(domain)
        self.name = getattr(self.m_domain, '__name__', domain)
        self.id = getattr(self.m_domain, '__id__')

        if not router:
            self.router = getattr('__router__', domain, '.routers')
        else:
            self.router = router

        self.m_router = importlib.import_module(self.router, domain)

        self.m_acl = importlib.import_module(f'{domain}.acl')

        self.config = config

        """
        if domain:
            m_domain = importlib.import_module(domain)
            if not router:
                router = getattr('__router__', domain, '.routers')
            m_domain_router = importlib.import_module(router, domain)
            m_domain_acl = importlib.import_module(f'{domain}.acl')

        if not(m_domain and m_domain_router and m_domain_acl):
            raise Exception('Cannot import domain')

        self.schema = domain_schema(m_domain)

        routes = [ Route('/', JSONRoute(self.schema)) ]
        """

        logger.info('HalfDomain creation %s %s', domain, config)
        super().__init__(
            routes=self.gen_domain_routes(),
            middleware=[
                (DomainMiddleware,
                    {
                    'domain': self.name,
                    'config': self.config
                    }
                )
            ]
        )

    @staticmethod
    def acls(domain):
        """ Returns the ACLS constant for the given domain
        """
        m_acl = importlib.import_module(f'{domain}.acl')
        try:
            return getattr(m_acl, 'ACLS')
        except AttributeError:
            raise Exception(f'Missing acl.ACLS constant in {domain} module')

    @staticmethod
    def acls_route(domain):
        d_res = {}
        m_acl = importlib.import_module(f'{domain}.acl')
        for acl_name, doc, order in HalfDomain.acls(domain):
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
        else:
            return acl.args_check(fct), params

    # @staticmethod
    # def gen_routes(m_router):
    #     """
    #     Yields the Route objects for a domain

    #     Parameters:
    #         m_domains: ModuleType

    #     Returns:
    #         Generator(HalfRoute)
    #     """
    #     """
    #     yield HalfRoute('/',
    #         JSONRoute(self.schema(self.m_domain)),
    #         [{'acl': acl.public}],
    #         'GET'
    #     )
    #     """

    #     for path, method, _, fct, params \
    #         in HalfDomain.gen_router_routes(m_router, []):

    #         yield HalfRoute(f'/{path}', fct, params, method)


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
            JSONRoute(self.domain_schema()),
            [{'acl': acl.public}],
            'GET'
        )

        for path, method, m_router, fct, params in HalfDomain.gen_router_routes(self.m_domain, []):
            yield HalfRoute(f'/{path}', fct, params, method)

    def domain_schema_dict(self) -> Dict:
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


    def domain_schema(self) -> Dict:
        schema = { **API_SCHEMA_DICT }
        schema['domain'] = {
            'name': self.name,
            'id': self.id,
            'version': getattr(self.m_domain, '__version__', ''),
            'patch_release': getattr(self.m_domain, '__patch_release__', ''),
            'routers': self.m_router.__name__,
            'acls': tuple(getattr(self.m_acl, 'ACLS', ()))
        }
        schema['paths'] = self.domain_schema_dict()
        return schema


    # def domain_schema_list(m_router: ModuleType) -> List:
    #     """ Schema as list, one row by route/acl
    #     Parameters:
    #
    #        m_router (ModuleType): The domain routers' module
    #
    #     Returns:
    #
    #        List[Tuple]: (path, verb, callable, doc, acls)
    #     """
    #     res = []
    #
    #     for path, verb, m_router, fct, parameters in gen_router_routes(m_router, []):
    #         for params in parameters:
    #             res.append((
    #                 path,
    #                 verb,
    #                 f'{m_router.__name__}:{fct.__name__}',
    #                 params.get('acl').__name__,
    #                 params.get('args', {}).get('required', []),
    #                 params.get('args', {}).get('optional', []),
    #                 params.get('out', [])
    #             ))
    #
    #     return res



