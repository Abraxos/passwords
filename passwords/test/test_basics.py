from pathlib import Path
from passwords.utils import package_path


MY_PATH = Path(__file__)


def test_basics():
    print("Hello, world!")
    assert True


def test_file_path():
    assert str(MY_PATH).endswith('passwords/passwords/test/test_basics.py')


def test_package_path():
    package = package_path(MY_PATH)
    assert str(package).endswith('/passwords')