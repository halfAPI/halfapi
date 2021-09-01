# HalfAPI

Base tools to develop comlex API with rights management.


## Dependencies

- python3
- python3-pip
- libgit2-dev
- starlette
- PyJWT
- click
- uvicorn
- orjson
- pyyaml


## Configuration

Configure HalfAPI in the file : .halfapi/config .

It's an **ini** file that contains at least two sections, project and domains.


### Project

The main configuration options without which HalfAPI cannot be run.

**name** : Project's name

**halfapi_version** : The HalfAPI version on which you work

**secret** : The file containing the secret to decode the user's tokens.

**port** : The port for the test server.

**loglevel** : The log level (info, debug, critical, ...)


### Domains

The name of the options should be the name of the domains' module, the value is the
submodule which contains the routers.

Example :

dummy_domain = .routers


## Usage

Develop an HalfAPI domain by following the examples located in
tests/dummy_domain . An HalfAPI domain should be an importable python module
that is available in the python path.

Run the project by using the `halfapi run` command.


## API Testing

@TODO


### Example

Check out the [sample project](https://github.com/halfAPI/halfapi_sample_project)
that helps you to build your own domain.


## Development

@TODO
