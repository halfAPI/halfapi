from uuid import uuid4
from halfapi.lib import acl
ACLS = {
    'GET' : [{'acl':acl.public}]
}
def get():
    """
    description: The pinnochio guy
    responses:
        200:
            description: test response
            content:
              application/json:
                schema:
                  $ref: "#/components/schemas/Pinnochio"
    """
    return {
        'id': str(uuid4()),
        'name': 'pinnochio',
        'nose_size': 42
    }
