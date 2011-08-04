#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from epio import __version__

requires = ['httplib2<=0.6.0']

try:
    import json
except ImportError:
    requires.append('simplejson')

setup(
    name='epio',
    version=__version__,
    description='The command-line client for the ep.io service',
    author='The ep.io Team',
    author_email='team@ep.io',
    url='http://www.ep.io/',
    packages = ['epio', 'epio.commands'],
    package_data = {
        'epio': ["skeleton/epio.ini"],
    },
    include_package_data=True,
    install_requires = requires,
    entry_points="""
    [console_scripts]
    epio = epio:main
    """,
    test_suite = 'nose.collector',
)
