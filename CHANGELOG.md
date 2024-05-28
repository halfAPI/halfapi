# HalfAPI

## 0.6.30

Dependencies updates 

- pyYAML v6.0.1
- starlette v0.37.2

Warning : the on_startup halfAPI argument is now removed, use the lifeSpan

## 0.6.29

### Dependencies

Starlette version bumped to 0.33.

## 0.6.28

### Dependencies

Starlette version bumped to 0.31 (had to disable a test to make it work but
seems not important).

### Development dependencies

Python 3.7 is no longer supported (openapi_spec_validator is not compatible).

If you are a developper, you should update dev dependencies in your virtual
environment.

### OpenAPI schemas

This release improves OpenAPI specification in routes, and gives a default
"parameters" field for routes that have path parameters.

Also, if you use halfAPI for multi-domain setups, you may be annoyed by the
change in the return value of the "/" route that differs from "/domain" route.

An HalfAPI instance should return one and only one OpenAPI Schema, so you can
rely on it to connect to other software.

The version number that is contained under the "info" dictionnary is now the "version"
of the Api domain, as specified in the domain dictionnary specified at the root
of the Domain.

The title field of the "info" dictionnary is now the Domain's name.

The ACLs list is now available under the "info.x-acls" attribute of the schema.
It is still accessible from the "/halfapi/acls" route.

#### Schema Components

You can now specify a dict in the domain's metadata dict that follows the
"components" key of an OpenAPI schema.

Use it to define models that are used in your API. You can see an exemple of
it's use in the "tests/dummy_domain/__init__.py" file.


### ACLs

The use of an "HEAD" request to check an ACL is now the norm. Please change all
the occurrences of your calls on theses routes with the GET method.


### CLI

Domain command update :

The `--conftest` flag is now allowed when running the `domain` command, it dumps the current configuration as a TOML string.

`halfapi domain --conftest my_domain`


The `--dry-run` flag was buggy and is now fixed when using the `domai ` command with the `--run` flag.


### Configuration

The `port` option in a `domain.my_domain` section in the TOML config file is now prefered to the one in the `project` section.

The `project` section is used as a default section for the whole configuration file. - Tests still have to be written -

The standard configuration precedence is fixed, in this order from the hight to the lower :

- Argument value (i.e. : --log-level)
- Environment value (i.e. : HALFAPI_LOGLEVEL)
- Configuration value under "domain" key
- Configuration value under "project" key
- Default configuration value given in the "DEFAULT_CONF" dictionary of halfapi/conf.py

### Logs

Small cleanup of the logs levels. If you don't want the config to be dumped, just set the HALFAPI_LOGLEVEL to something different than "DEBUG".

### Fixes

- Check an ACL based on a decorator on "/halfapi/acls/MY_ACL"

## 0.6.27

### Breaking changes

- ACLs definition can now include a "public" parameter that defines if there should be an automatic creation of a route to check this acls
- /halfapi/acls does not return the "result", it just returns if there is a public route to check the ACL on /halfapi/acls/acl_name
=======
argument of starlette instead.
>>>>>>> a8c59c6 ([release] halfapi 0.6.27)

## 0.6.26

- Adds the "base_url", "cookies" and "url" to the "halfapi" argument of route definitions

## 0.6.25

- Deletes the "Authorization" cookie on authentication error
- Do not raise an exception on signature expiration, use "Nobody" user instead

## 0.6.24

- Uses the "Authorization" cookie to read authentication token additionnaly to the "Authorization" header
- CLI : allows to run a single domain using the "halfapi domain --run domain_name" command

## 0.6.23

Dependency update version

- starlette v0.23
- orjson v3.8.5
- click v8
- pyJWT v2.6
- pyYAML v6
- toml v0.10

## 0.6.22

- IMPORTANT : Fix bug introduced with 0.6.20 (fix arguments handling)
- BREAKING : A domain should now include it's meta datas in a "domain" dictionary located in the __init__.py file of the domain's root. Consider looking in 'tests/dummy_domain/__init__.py'
- Add *html* return type as default argument ret_type
- Add *txt* return type
- Log unhandled exceptions
- Log HTTPException with statuscode 500 as critical
- PyJWT >=2.4.0,<2.5.0


## 0.6.21

- Store only domain's config in halfapi['config'] 
- Should run halfapi domain with config_file argument
- Testing : You can specify a "MODULE" attribute to point out the path to the Api's base module
- Testing : You can specify a "CONFIG" attribute to set the domain's testing configuration
- Environment : HALFAPI_DOMAIN_MODULE can be set to specify Api's base module
- Config : 'module' attribute can be set to specify Api's base module

## 0.6.20

- Fix arguments handling

## 0.6.19

- Allow file sending in multipart request (#32)
- Add python-multipart dependency

## 0.6.18

- Fix config coming from .halfapi/config when using HALFAPI_DOMAIN_NAME environment variable

## 0.6.17

- Fix 0.6.16
- Errata : HALFAPI_DOMAIN is HALFAPI_DOMAIN_NAME
- Testing : You can now specify "MODULE" class attribute for your "test_domain"
  subclasses

## 0.6.16

- The definition of "HALFAPI_DOMAIN_MODULE" environment variable allows to
  specify the base module for a domain structure. It is formatted as a python
  import path.
  The "HALFAPI_DOMAIN" specifies the "name" of the module

## 0.6.15

- Allows to define a "__acl__" variable in the API module's __init__.py, to
  specify how to import the acl lib. You can also specify "acl" in the domain's
  config

## 0.6.14

- Add XLSXResponse (with format argument set to "xlsx"), to return .xlsx files

## 0.6.13

- (rollback from 0.6.12) Remove pytest from dependencies in Docker file and
  remove tests
- (dep) Add "packaging" dependency
- Add dependency check capability when instantiating a domain (__deps__
  variable, see in dummy_domain)

## 0.6.12

- Installs pytest with dependencies in Docker image, tests when building image

## 0.6.11

- Fix "request" has no "path_params" attribute bug

## 0.6.10

- Add "x-out" field in HTTP headers when "out" parameters are specified for a
  route
- Add "out" kwarg for not-async functions that specify it

## 0.6.9

- Hide data fields in args_check logs

## 0.6.8

- Fix testing lib for domains (add default secret and debug option)

## 0.6.2

- Domains now need to include the following variables in their __init__.py
    - __name__ (str, optional)
    - __id__ (str, optional)
- halfapi domain


## 0.1.0

- Mounts domain routers with their ACLs as decorator
- Configuration example files for systemd and a system-wide halfapi install
- Runs projects
- Handles JWT authentication middleware
