import click
from flask import Flask, jsonify, request
from configparser import ConfigParser
from pathlib import Path

from .utils import package_path
from .client_auth_app import ClientAuthApplication

MY_PATH = Path(__file__)
PACKAGE_PATH = package_path(MY_PATH)


def configure_app(app, config):
    # app.config.update(
    #     SOLVER_HOSTNAME=config['client_api']['xmlrpc_solver_hostname'],
    #     SOLVER_PORT=config['client_api']['xmlrpc_solver_port']
    # )
    return app


APP = Flask(__name__)


def api_v0_1(route):
    return '/api/v0.1/{}'.format(route)


@APP.route(api_v0_1('hello'), methods=['GET', 'PUT'])
def hello():
    """Receives a sudoku to solve and returns a solution"""
    return "Hello, world!"


@APP.route(api_v0_1('headers'))
def headers():
    """Basic function"""
    return jsonify({'X-USER': request.headers['X-USER'],
                    'X-ISSUER': request.headers['X-ISSUER'],
                    'X-NOT_BEFORE': request.headers['X-NOT_BEFORE'],
                    'X-NOT_AFTER': request.headers['X-NOT_AFTER']})


@click.command()
@click.argument('config-file')
def run_app_server(config_file):
    """Launches Passwords REST API (without client authentication) in a gunicorn server"""
    config_file = Path(config_file)
    config = ConfigParser()
    config.read(config_file)

    ca_path = config_file.parent / config['webapp']['ca']
    cert_path = config_file.parent / config['webapp']['cert']
    key_path = config_file.parent / config['webapp']['key']
    hostname = config['webapp']['hostname']
    port = config['webapp']['port']

    configure_app(APP, config)
    ClientAuthApplication(APP, ca_path, cert_path, key_path, hostname, port).run()


if __name__ == '__main__':
    run_app_server()
