import os
from configparser import ConfigParser
from half_orm.model import Model

import click
from .cli import cli

@cli.command()
def init():
    """
    The "halfapi init" command for hop projects
    """
    hop_conf_path = os.path.join('.hop', 'config')
    config = ConfigParser()
    config.read([ hop_conf_path ])

    assert os.path.isdir(config.get('halfORM', 'package_name'))

    model = Model(config.get('halfORM', 'package_name'))

    import halfapi
    halfapi_path = list(halfapi.__path__)[0]
    sql_path = os.path.join(halfapi_path, 'sql', 'api.sql')
    
    with open(sql_path, 'r') as sql_file:
        for query in ''.join(sql_file.readlines()).split(';'):
            if len(query.strip()) == 0:
                continue
            model.execute_query(query.strip())

    click.echo('halfapi schema has been initialized')
    click.echo('use halfapi route command to create your first route')
    click.echo('example : halfapi route add')
