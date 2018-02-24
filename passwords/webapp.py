import click
from flask import Flask, jsonify, request
from configparser import ConfigParser
from pathlib import Path
from voluptuous import MultipleInvalid
import psycopg2
from psycopg2.extras import NamedTupleCursor
import arrow
from psycopg2.sql import SQL, Literal

from .utils import package_path
from .client_auth_app import ClientAuthApplication
from .validation import SHA512_SCHEMA, InvalidInput

MY_PATH = Path(__file__)
PACKAGE_PATH = package_path(MY_PATH)


def configure_app(app, config):
    app.config.update(
        DB_HOSTNAME=config['database']['hostname'],
        DB_USERNAME=config['database']['username'],
        DB_PASSWORD=config['database']['password'],
        DB_NAME='passwords' if 'db_name' not in config['database'] else config['database']['db_name']
    )
    return app


# Queries
SHA_512_EXISTS = SQL("SELECT EXISTS(SELECT 1 FROM passwords.account_passwords WHERE passwd_hash={0})")


APP = Flask(__name__)


@APP.errorhandler(InvalidInput)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def api_v0_1(route):
    return '/api/v0.1/{}'.format(route)


def with_metadata(data):
    return {'metadata': {'timestamp': arrow.utcnow().timestamp},
            'data': data}


def known_password_reply(sha512: str, is_known: bool):
    return with_metadata({'password_sha512': sha512,
                          'is_known': is_known})


@APP.route(api_v0_1('hello'), methods=['GET'])
def hello():
    """Receives a sudoku to solve and returns a solution"""
    return jsonify(with_metadata("Hello, world!"))


@APP.route(api_v0_1('headers'))
def headers():
    """Basic function"""
    return jsonify(with_metadata({'X-USER': request.headers['X-USER'],
                                  'X-ISSUER': request.headers['X-ISSUER'],
                                  'X-NOT_BEFORE': request.headers['X-NOT_BEFORE'],
                                  'X-NOT_AFTER': request.headers['X-NOT_AFTER']}))


@APP.route(api_v0_1('is_password_known/<sha512>'), methods=['GET'])
def is_password_known(sha512: str):
    """Look up the SHA512 in the database and return True if it exists"""
    try:
        SHA512_SCHEMA(sha512)
    except MultipleInvalid as e:
        raise InvalidInput(e.msg)

    with psycopg2.connect("dbname='{}' user='{}' host='{}' password='{}'"
                          .format(APP.config['DB_NAME'],
                                  APP.config['DB_USERNAME'],
                                  APP.config['DB_HOSTNAME'],
                                  APP.config['DB_PASSWORD'])) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute(SHA_512_EXISTS.format(Literal(sha512)))
            result = cursor.fetchone()
            return jsonify(known_password_reply(sha512, result.exists))


@APP.route(api_v0_1('search/account/<account_name>'))
def search_account_name(account_name: str):
    """Look up a specific account substring in the database and return all entries. WARNING: This function is dangerous.
       Can be used to search for people's passwords. Control access to it very tightly."""
    pass


@APP.route(api_v0_1('search/password/<password>'))
def search_password_name(password: str):
    """Look up a specific password substring in the database and return all entries. WARNING: This function is dangerous.
       Can be used to search for people's passwords. Control access to it very tightly."""
    pass


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
