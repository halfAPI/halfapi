create schema api;

create type verb as enum ('POST', 'GET', 'PUT', 'PATCH', 'DELETE');

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
    keys text[],
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
