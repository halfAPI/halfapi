#!/usr/bin/env python3
"""
cli/domain.py Defines the "halfapi domain" cli commands
"""
# builtins
import logging
import sys

import click


from .cli import cli
from ..conf import config, write_config, DOMAINSDICT

from ..lib.schemas import schema_dict_dom


logger = logging.getLogger('halfapi')

#################
# domain create #
#################
def create_domain(domain_name: str, module_path: str):
    logger.info('Will add **%s** (%s) to current halfAPI project', 
            domain_name, module_path)

    if domain_name in DOMAINSDICT():
        logger.warning('Domain **%s** is already in project')
        sys.exit(1)

    if not config.has_section('domains'):
        config.add_section('domains')

    config.set('domains', domain_name, module_path)
    write_config()


###############
# domain read #
###############
def list_routes(domain, m_dom):
    """
    Echoes the list of the **m_dom** active routes
    """

    click.echo(f'\nDomain : {domain}')

    for key, item in schema_dict_dom({domain: m_dom}).get('paths', {}).items():
        methods = '|'.join(list(item.keys()))
        click.echo(f'{key} : {methods}')


def list_api_routes():
    """
    Echoes the list of all active domains.
    """
    
    click.echo('# API Routes')
    for domain, m_dom in DOMAINSDICT().items():
        list_routes(domain, m_dom)


@click.option('--read',default=False, is_flag=True)
@click.option('--create',default=False, is_flag=True)
@click.option('--update',default=False, is_flag=True)
@click.option('--delete',default=False, is_flag=True)
@click.option('--domains',default=None)
@cli.command()
def domain(domains, delete, update, create, read):  #, domains, read, create, update, delete):
    """
    The "halfapi domain" command

    Parameters:
        domain (List[str]|None): The list of the domains to list/update

        The parameter has a misleading name as it is a multiple option
        but this would be strange to use it several times named as "domains"

        update (boolean): If set, update the database for the selected domains
    """

    if not domains:
        if create:
            # TODO: Connect to the create_domain function
            raise NotImplementedError

        domains = DOMAINSDICT().keys()
    else:
        domains_ = []
        for domain_name in domains.split(','):
            if domain_name in DOMAINSDICT().keys():
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
            list_api_routes()
