# HalfAPI

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
