#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

from setuptools import setup, find_packages

import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(package, "__init__.py")) as f:
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", f.read()).group(1)


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
    url="https://github.com/halfAPI/halfapi",
    description="Core to write deep APIs using a module's tree",
    author="Maxime ALVES",
    author_email="maxime@freepoteries.fr",
    license="GPLv3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=get_packages(module_name),
    python_requires=">=3.8",
    install_requires=[
        "PyJWT>=2.4.0,<2.5.0",
        "starlette>=0.17,<0.18",
        "click>=7.1,<8",
        "uvicorn>=0.13,<1",
        "orjson>=3.4.7,<4",
        "pyyaml>=5.3.1,<6",
        "timing-asgi>=0.2.1,<1",
        "schema>=0.7.4,<1",
        "toml>=0.7.1,<0.8",
        "packaging>=19.0",
        "python-multipart"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ],
    extras_require={
        "tests":[
            "pytest>=7,<8",
            "requests",
            "pytest-asyncio",
            "pylint"
        ],
        "pyexcel":[
            "pyexcel",
            "pyexcel-ods3",
            "pyexcel-xlsx"
        ]
    },
    entry_points={
        "console_scripts":[
            "halfapi=halfapi.cli.cli:cli"
        ]
    },
    keywords="web-api development boilerplate",
    project_urls={
        "Source": "https://github.com/halfAPI/halfapi",
    }
)
