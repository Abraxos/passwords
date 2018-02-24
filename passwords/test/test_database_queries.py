from passwords.webapp import APP, api_v0_1, configure_app
import json
import pytest
# from unittest import mock
# from pytest_mock import mocker
from collections import namedtuple
import psycopg2


APP.testing = True


IsKnownResult = namedtuple('IsKnownResult', ['exists'])


@pytest.mark.parametrize("test_input, expected_result", [
    ('bed4efa1d4fdbd954bd3705d6a2a78270ec9a52ecfbfb010c61862af5c76af1761ffeb1aef'
     '6aca1bf5d02b3781aa854fabd2b69c790de74e17ecfec3cb6ac4bf', True),  # hash of password123
    ('60d44004163ccd939f067d09a8f257d2b664a33be716ebbd32ce00531736da94138a94b46a'
     '41420a4602d710f50b6f3ed6234768168b60a67dc394191a644669', False),
])
def test_known_password(mocker, test_input: str, expected_result: bool):
    configure_app(APP, {'database': {'hostname': 'some-host',
                                     'db_name': 'passwords',
                                     'username': 'eugene',
                                     'password': 'changeit'}})
    mocker.patch.object(psycopg2, 'connect')
    psycopg2.connect().__enter__().cursor().__enter__().fetchone\
        .return_value = IsKnownResult(expected_result)

    app = APP.test_client()
    r = app.get(api_v0_1('is_password_known/{}').format(test_input))

    assert r.status_code == 200
    r = json.loads(r.data, encoding='utf-8')
    assert r['data']['is_known'] == expected_result
