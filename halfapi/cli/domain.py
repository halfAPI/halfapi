#!/usr/bin/env python3
"""
cli/domain.py Defines the "halfapi domain" cli commands
"""

# builtins
import logging
import click


from .cli import cli
from ..conf import DOMAINS, DOMAINSDICT

from ..lib.schemas import schema_dict_dom


logger = logging.getLogger('halfapi')

#################
# domain create #
#################
def create_domain():
    """
    TODO: Implement function to create (add) domain to a project through cli
    """
    raise NotImplementedError


###############
# domain read #
###############
def list_routes(domain_name):
    """
    Echoes the list of the **domain_name** active routes
    """

    click.echo(f'\nDomain : {domain}')

    m_dom = DOMAINSDICT[domain_name]
    for key, item in schema_dict_dom(m_dom).get('paths', {}).items():
        methods = '|'.join(list(item.keys()))
        click.echo(f'{key} : {methods}')


@click.option('--read',default=False, is_flag=True)
@click.option('--create',default=False, is_flag=True)
@click.option('--update',default=False, is_flag=True)
@click.option('--delete',default=False, is_flag=True)
@click.option('--domains',default=None)
@cli.command()
def domain(domains, delete, update, create, read):  #, domains, read, create, update, delete):
    """
    Lists routes for the specified domains, or update them in the database

    Parameters:
        domain (List[str]|None): The list of the domains to list/update

        The parameter has a misleading name as it is a multiple option
        but this would be strange to use it several times named as "domains"

        update (boolean): If set, update the database for the selected domains
    """

    if not domains:
        if create:
            create_domain()

        domains = DOMAINS
    else:
        domains_ = []
        for domain_name in domains.split(','):
            if domain_name in DOMAINS:
                domains_.append(domain_name)
                continue

            click.echo(
                f'Domain {domain_name}s is not activated in the configuration')

        domains = domains_

    for domain_name in domains:
        if update:
            raise NotImplementedError
        if delete:
            raise NotImplementedError

        if read:
            list_routes(domain_name)
