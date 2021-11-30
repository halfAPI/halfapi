# HalfAPI

Base tools to develop complex API with rights management.

This project was developped by Maxime Alves and Joël Maïzi. The name was chosen
to reference [HalfORM](https://github.com/collorg/halfORM), a project written by Joël Maïzi.


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

You can try the dummy_domain with the following command.

```
python -m halfapi routes --export --noheader dummy_domain.routers | python -m halfapi run -
```


## API Testing

@TODO


### Example

Check out the [sample project](https://github.com/halfAPI/halfapi_sample_project)
that helps you to build your own domain.


## Development

@TODO
