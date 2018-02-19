"""Setup file for the passwords webapp."""
from setuptools import setup, find_packages

with open('README.md') as f:
    README = f.read()

with open('requirements.txt') as f:
    REQUIREMENTS = f.readlines()

setup(
    name='passwords',
    version='0.1.0',
    description="A flask REST API for checking whether a password is already"
                "public and shouldn't be used",
    long_description=README,
    author='Eugene Kovalev',
    author_email='euge.kovalev@gmail.com',
    url='https://github.com/Abraxos/passwords',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=REQUIREMENTS,
    entry_points={'console_scripts': ['passwords-webapp=passwords.webapp:run_app_server']},
)
