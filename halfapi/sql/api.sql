CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS halfapi;

DROP TABLE IF EXISTS halfapi.endpoint;
DROP TABLE IF EXISTS halfapi.parameter;
DROP TABLE IF EXISTS halfapi.segment;
DROP TABLE IF EXISTS halfapi.base_table;

CREATE TABLE halfapi.segment (
    id uuid DEFAULT public.gen_random_uuid(),
    fqtn text,
    PRIMARY KEY (id),
    name text,
    parent uuid DEFAULT NULL,
    UNIQUE(name, parent)
);

ALTER TABLE halfapi.segment ADD CONSTRAINT
    segment_parent_fkey FOREIGN KEY (parent) REFERENCES halfapi.segment(id);

DROP TABLE IF EXISTS halfapi.type;
CREATE TABLE halfapi.type (
    name text,
    PRIMARY KEY (name)
);

CREATE TABLE halfapi.parameter (
    type text REFERENCES halfapi.type(name)
) INHERITS (halfapi.segment);

DROP TABLE IF EXISTS halfapi.endpoint_type;
CREATE TABLE halfapi.endpoint_type (
    name text,
    PRIMARY KEY (name)
);

DROP TYPE IF EXISTS method;
CREATE TYPE method AS ENUM ('get', 'post', 'patch', 'put', 'delete');
CREATE TABLE halfapi.endpoint (
    method method,
    type text,
    segment uuid NOT NULL,
    PRIMARY KEY (method, segment)
);

ALTER TABLE halfapi.endpoint ADD CONSTRAINT
    endpoint_segment_id FOREIGN KEY (segment) REFERENCES halfapi.segment(id);

ALTER TABLE halfapi.endpoint ADD CONSTRAINT
    endpoint_type_name FOREIGN KEY (type) REFERENCES halfapi.endpoint_type(name);
