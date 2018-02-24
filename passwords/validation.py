import re
from voluptuous import Schema, Invalid


SHA516_PAT = re.compile('^[A-Fa-f0-9]{128}$')


def is_sha512(sha512_candidate: str) -> bool:
    if not isinstance(sha512_candidate, str):
        raise Invalid('{} is not a string'.format(sha512_candidate))
    elif not SHA516_PAT.match(sha512_candidate):
        raise Invalid('{} is not a valid SHA512 hash'.format(sha512_candidate))
    return True


class InvalidInput(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code if status_code is not None else self.status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


# Validation Schemas
SHA512_SCHEMA = Schema(is_sha512)
