#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, "__init__.py"))
    ]


from setuptools import setup, find_packages
module_name="dummy_domain"
setup(
    name=module_name,
    version='0',
    url="https://gite.lirmm.fr/malves/halfapi",
    packages=get_packages(module_name),
    python_requires=">=3.7",
    install_requires=[]
)
