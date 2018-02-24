import pytest
import json

from passwords.webapp import APP, api_v0_1


APP.testing = True


def test_hello():
    app = APP.test_client()
    r = json.loads(app.get(api_v0_1('hello')).data, encoding='utf-8')
    assert r['data'] == 'Hello, world!'


@pytest.mark.parametrize("test_input,expected_success,expected_status_code", [
    ("stuff", False, 400),
    (1, False, 400),
    (True, False, 400),
    ('ca0ddbf644f3e12a7790072e82c604c920a064ea5e678581afab6e2887e', False, 400),
    ('ca0ddbf644f3e12a7790072e82c604c920a064ea5e678581afab6e2887e02bdaff6a7ba2bb'
     '8e2954e66ffc33fd84885fbd871165f45fec9a6f4d96083f4c8dc2a', False, 400),
    ('ca0ddbf644f3e12a7790072e82c604c920a064ea5e678581afab6e2887e02bdaxf6a7ba2bb'
     '8e2954e66ffc33fd84885fbd871165f45fec9a6f4d96083f4c8dc2', False, 400),
])
def test_sha512_validation(test_input, expected_success: bool, expected_status_code: int):
    app = APP.test_client()
    r = app.get(api_v0_1('is_password_known/{}').format(test_input))
    print(r.data)
    assert r.status_code == expected_status_code
    r = json.loads(r.data, encoding='utf-8')
    if not expected_success:
        assert "message" in r
