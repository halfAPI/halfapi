from uuid import UUID
from halfapi.lib import acl
ACLS = {
  'GET': [{'acl': acl.public}]
}

def get(first, second, third):
  """
  description: a Test route for path parameters
  responses:
    200:
      description: The test passed!
    500:
      description: The test did not pass :(
  """
  assert isintance(first, str)
  assert isintance(second, UUID)
  assert isintance(third, int)

  return ''
