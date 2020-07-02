create schema api;

create type verb as enum ('POST', 'GET', 'PUT', 'DELETE');

create table api.version (
    name text primary key,
    server cidr not null default '127.0.0.1',
    port integer not null
);

create table api.domain (
    version text references api.version(name),
    name text,
    primary key (version, name)
);

create table api.route (
    path text, -- relative to /api/<version>/<domain>
    version text,
    domain text,
    primary key (path, domain, version)
);

alter table api.route add constraint route_domain_fkey foreign key (version, domain) references api.domain(version, name) on update cascade on delete cascade;

create table api.acl_function (
    name text,
    description text,
    version text,
    domain text,
    primary key (name, version, domain)
);

alter table api.acl_function add constraint acl_function_domain_fkey foreign key (version, domain) references api.domain(version, name) on update cascade on delete cascade;

create table api.acl (
    name text,
    http_verb verb,
    path text not null,
    version text,
    domain text not null,
    function text not null,
    primary key (name, version, domain, function)
);

alter table api.acl add constraint acl_route_fkey foreign key (path, version, domain) references api.route(path, version, domain) on update cascade on delete cascade;
alter table api.acl add constraint acl_function_fkey foreign key (function, version, domain) references api.acl_function(name, version, domain) on update cascade on delete cascade;

create schema "api.view";

create view "api.view".route as
select
    route.*,
    version.name,
    version.server,
    version.port,
    '/'::text || route.domain || route.path AS abs_path
from
    api.route
    join api.domain on
    route.domain = domain.name
    join api.version on
    domain.version = version.name;

create view "api.view".acl as
select
    acl.*,
    acl_function.name as acl_function_name,
    '/'::text || acl.domain || acl.path AS abs_path
from
    api.acl
    join api.acl_function on
    acl.function = acl_function.name;
