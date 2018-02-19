from passwords.webapp import ClientAuthApplication, APP, api_v0_1
from passwords.utils import package_path
from contextlib import contextmanager
from pathlib import Path
from multiprocessing import Process
import requests
from time import sleep
import pytest


MY_PATH = Path(__file__)
PACKAGE_PATH = package_path(MY_PATH)


@contextmanager
def local_server(key_path: Path, cert_path: Path, ca_path: Path, port=8080):
    """A context manager that spins up a client-auth gunicorn server as a
       separate process and then closes it when needed. Configured for
       testing with a low timeout."""
    def run_server():
        gunicorn_app = ClientAuthApplication(APP, ca_path, cert_path, key_path,
                                             hostname='localhost', port=port,
                                             num_workers=1, timeout=2)
        gunicorn_app.run()
    server_process = Process(target=run_server)
    try:
        server_process.start()
        sleep(0.4)
        yield 'https://localhost:{}'.format(port)
    finally:
        server_process.terminate()


def test_client_auth_with_same_credentials():
    """If someone attempts to make a connection using the same exact credentials as the server, that connection
       should succeed and the headers should be set appropriately."""
    key_path = PACKAGE_PATH / 'passwords/test/resources/server/server.key'
    ca_path = PACKAGE_PATH / 'passwords/test/resources/server/ca.crt'
    cert_path = PACKAGE_PATH / 'passwords/test/resources/server/server.crt'
    with local_server(key_path, cert_path, ca_path) as host:
        result = requests.get(host + api_v0_1('hello'), verify=str(ca_path), cert=(cert_path, key_path))
        assert result.status_code == 200
        result = requests.get(host + api_v0_1('headers'), verify=str(ca_path), cert=(cert_path, key_path))
        assert result.json()['X-ISSUER'] == 'Kovalev Systems CA'
        assert result.json()['X-USER'] == 'Eugenes Test Server'


def test_client_auth_with_valid_credentials():
    """If someone attempts to make a connection using valid client credentials, that connection
       should succeed and the headers should be set appropriately."""
    server_key_path = PACKAGE_PATH / 'passwords/test/resources/server/server.key'
    ca_path = PACKAGE_PATH / 'passwords/test/resources/server/ca.crt'
    server_cert_path = PACKAGE_PATH / 'passwords/test/resources/server/server.crt'
    alice_key_path = PACKAGE_PATH / 'passwords/test/resources/alice/alice.key'
    alice_cert_path = PACKAGE_PATH / 'passwords/test/resources/alice/alice.crt'
    with local_server(server_key_path, server_cert_path, ca_path) as host:
        result = requests.get(host + api_v0_1('hello'), verify=str(ca_path), cert=(alice_cert_path, alice_key_path))
        assert result.status_code == 200
        result = requests.get(host + api_v0_1('headers'), verify=str(ca_path), cert=(alice_cert_path, alice_key_path))
        assert result.json()['X-ISSUER'] == 'Kovalev Systems CA'
        assert result.json()['X-USER'] == 'Alice'


@pytest.mark.xfail(raises=requests.exceptions.SSLError)
def test_self_signed_cert_client():
    """If someone attempts to make a connection using a self-signed certificate, this should fail."""
    server_key_path = PACKAGE_PATH / 'passwords/test/resources/server/server.key'
    ca_path = PACKAGE_PATH / 'passwords/test/resources/server/ca.crt'
    server_cert_path = PACKAGE_PATH / 'passwords/test/resources/server/server.crt'
    eve_key_path = PACKAGE_PATH / 'passwords/test/resources/eve/eve.key'
    eve_cert_path = PACKAGE_PATH / 'passwords/test/resources/eve/eve.crt'
    with local_server(server_key_path, server_cert_path, ca_path) as host:
        result = requests.get(host + api_v0_1('hello'), verify=str(ca_path), cert=(eve_cert_path, eve_key_path))
        assert result.status_code == 200


@pytest.mark.xfail(raises=requests.exceptions.SSLError)
def test_malicious_ca_client():
    """If someone attempts to make a connection using a certificate with the same CA name, but incorrect signature
       this should fail."""
    server_key_path = PACKAGE_PATH / 'passwords/test/resources/server/server.key'
    ca_path = PACKAGE_PATH / 'passwords/test/resources/server/ca.crt'
    server_cert_path = PACKAGE_PATH / 'passwords/test/resources/server/server.crt'
    mallory_key_path = PACKAGE_PATH / 'passwords/test/resources/mallory/mallory.key'
    mallory_cert_path = PACKAGE_PATH / 'passwords/test/resources/mallory/mallory.crt'
    with local_server(server_key_path, server_cert_path, ca_path) as host:
        result = requests.get(host + api_v0_1('hello'), verify=str(ca_path), cert=(mallory_cert_path, mallory_key_path))
        assert result.status_code == 200
