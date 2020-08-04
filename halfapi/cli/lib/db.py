import click
from half_orm.model import Model, CONF_DIR
from half_orm.model_errors import MissingConfigFile
import psycopg2
import subprocess

_DB_SCHEMA = """
create schema api;

create type verb as enum ('POST', 'GET', 'PUT', 'DELETE');

create table api.domain (
    name text,
    primary key (name)
);

create table api.router (
    name text,
    domain text,
    primary key (name, domain)
);

alter table api.router add constraint router_domain_fkey foreign key (domain) references api.domain(name) on update cascade on delete cascade;

create table api.route (
    http_verb verb,
    path text, -- relative to /<domain>/<router>
    fct_name text,
    router text,
    domain text,
    primary key (http_verb, path, router, domain)
);

alter table api.route add constraint route_router_fkey foreign key (router, domain) references api.router(name, domain) on update cascade on delete cascade;

create table api.acl_function (
    name text,
    description text,
    domain text,
    primary key (name, domain)
);

alter table api.acl_function add constraint acl_function_domain_fkey foreign key (domain) references api.domain(name) on update cascade on delete cascade;

create table api.acl (
    http_verb verb,
    path text not null,
    router text,
    domain text,
    acl_fct_name text,
    primary key (http_verb, path, router, domain, acl_fct_name)
);

alter table api.acl add constraint acl_route_fkey foreign key (http_verb, path,
router, domain) references api.route(http_verb, path, router, domain) on update cascade on delete cascade;
alter table api.acl add constraint acl_function_fkey foreign key (acl_fct_name, domain) references api.acl_function(name, domain) on update cascade on delete cascade;

create schema "api.view";

create view "api.view".route as
select
    route.*,
    '/'::text || route.domain || '/'::text || route.router || route.path AS abs_path
from
    api.route
    join api.domain on
    route.domain = domain.name
;

create view "api.view".acl as
select
    acl.*,
    '/'::text || route.domain || '/'::text || route.router || route.path AS abs_path
from
    api.acl
    join api.acl_function on
    acl.acl_fct_name = acl_function.name
    join api.route on
    acl.domain = route.domain
    and acl.router = route.router
    and acl.path = route.path;
"""

HOP_CONF = """[database]
name = {}
"""

class ProjectDB:
    def __init__(self, project_name):
        self.__project_name = project_name
        self.__db_name = f'halfapi_{self.__project_name}'
        self.__db = self._get_db()

    def _get_db(self):
        from subprocess import PIPE
        hop_conf_file = f'{CONF_DIR}/{self.__db_name}'
        try:
            return Model(self.__db_name)
        except psycopg2.OperationalError as err:
            "créer la base de données"
            ret = subprocess.run(['/usr/bin/createdb', self.__db_name])
            if ret.returncode != 0:
                raise Exception(f"Can't create {self.__db_name}")
        except MissingConfigFile:
            print(f"demande validation de {CONF_DIR} {self.__db_name}")
            print("demande validation création de fichier de CONF")
            open(hop_conf_file, 'w').write(HOP_CONF.format(self.__db_name))
        return self._get_db()

    def init(self):
        """
        """
        self.__db.execute_query(_DB_SCHEMA)
        self.__db._connection.close()

