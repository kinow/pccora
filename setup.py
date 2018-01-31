#!/usr/bin/env python

from setuptools import setup
import unittest

def pccora_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite

test_requirements = []

setup(name='pccora',
      version='0.2',
      description='PC-CORA sounding data files parser for Python',
      url='http://github.com/niwa/pccora',
      author='Bruno P. Kinoshita',
      author_email='brunodepaulak@yahoo.com.br',
      license='MIT',
      keywords = ['sounding file', 'radiosonde', 'vaisala', 'pccora'],
      packages=['pccora'],
      zip_safe=False,
      tests_require = test_requirements,
      test_suite='setup.pccora_test_suite',
      install_requires = [
        'construct==2.5.1'
      ] + test_requirements)
