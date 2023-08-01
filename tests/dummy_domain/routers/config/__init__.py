from ... import acl
from halfapi.logging import logger

ACLS = {
    'GET' : [
        {'acl':acl.public},
        {'acl':acl.random},
    ]
}

def get(halfapi):
    """
    description:
        returns the configuration of the domain
    responses:
        200:
            description: test response
    """
    logger.error('%s', halfapi)
    # TODO: Remove in 0.7.0
    try:
        assert 'test' in halfapi['config']['domain']['dummy_domain']['config']
    except AssertionError as exc:
        logger.error('No TEST in halfapi[config][domain][dummy_domain][config]')
        raise exc

    try:
        assert 'test' in halfapi['config']
    except AssertionError as exc:
        logger.error('No TEST in halfapi[config]')
        raise exc

    return halfapi['config']
