from multiprocessing import cpu_count
from pathlib import Path


def number_of_workers():
    return (cpu_count() * 2) + 1


def package_path(my_path: Path):
    return next(parent for parent in my_path.parents if parent.name == 'passwords').parent
