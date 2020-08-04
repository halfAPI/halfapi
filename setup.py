#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

from setuptools import setup, find_packages

import pathlib

def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(package, "__init__.py")) as f:
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", f.read()).group(1)


def get_long_description():
    """
    Return the README.
    """
    here = pathlib.Path(__file__).parent.resolve()
    long_description = (here / 'README.md').read_text(encoding='utf-8')

def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, "__init__.py"))
    ]

module_name="halfapi"
setup(
    name=module_name,
    version=get_version(module_name),
    url="https://gite.lirmm.fr/malves/halfapi",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    packages=get_packages(module_name),
    python_requires=">=3.7",
    install_requires=[
        "jwt",
        "starlette",
        "half_orm @ git+ssh://git@gite.lirmm.fr/maizi/halfORM.git",
        "click",
        "pygit2",
        "uvicorn"
    ],
    extras_require={
        "tests":[
            "pytest",
            "requests"
        ]
    },
    entry_points={
        "console_scripts":[
            "halfapi=halfapi.cli:cli"
        ]
    }
)