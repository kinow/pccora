#!/usr/bin/env python

import unittest

from setuptools import setup


def pccora_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


test_requirements = []

install_requires = [
    'construct==2.5.1'
]

extras_require = {
    'scripts_linux': [
        'jinja2',
        'netcdf4',
        'numpy',
        'pytz'
    ],
    'scripts_win32': [
        'plac'
    ]
}

setup(
    name='pccora',
    version='0.3',
    description='PC-CORA sounding data files parser for Python',
    url='http://github.com/niwa/pccora',
    author='Bruno P. Kinoshita',
    author_email='brunodepaulak@yahoo.com.br',
    license='MIT',
    keywords=['sounding file', 'radiosonde', 'vaisala', 'pccora', 'atmosphere'],
    packages=['pccora'],
    zip_safe=False,
    tests_require=test_requirements,
    install_requires=install_requires,
    extras_require=extras_require
)
