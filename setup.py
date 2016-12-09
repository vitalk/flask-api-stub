#!/usr/bin/env python
# -*- coding: utf8 -*-
import io
import os
from setuptools import (
    find_packages, setup
)


def read(*parts):
    """Reads the content of the file located at path created from *parts*."""
    try:
        return io.open(os.path.join(*parts), 'r', encoding='utf-8').read()
    except IOError:
        return ''


requirements = read('requirements.txt').splitlines()


setup(
    name='flask_api_stub',
    version='0.1.0',
    description='Simple REST API example built on top of Flask',
    author='Vital Kudzelka',
    author_email='vital.kudzelka@gmail.com',
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        "Private :: Do Not Upload",
        "Programming Language :: Python",
        "Framework :: Flask",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
    ]
)
