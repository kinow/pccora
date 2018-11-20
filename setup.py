#!/usr/bin/env python

from setuptools import setup


test_requirements = [
    'coverage',
    'pytest-cov',
    'pytest',
    'pycodestyle',
    'virtualenv',
    'tox-travis'
]

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

extras_require['all'] = extras_require['scripts_linux'] + extras_require['scripts_win32']

setup(
    name='pccora',
    version='0.3',
    description='PC-CORA sounding data files parser for Python',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    url='http://github.com/niwa/pccora',
    author='Bruno P. Kinoshita',
    author_email='brunodepaulak@yahoo.com.br',
    license='MIT',
    platforms="any",
    python_requires=">=3.3",
    keywords=['sounding file', 'radiosonde', 'vaisala', 'pccora', 'atmosphere'],
    packages=['pccora'],
    zip_safe=False,
    tests_require=test_requirements,
    install_requires=install_requires,
    extras_require=extras_require,
    setup_requires=['pytest-runner'],
    project_urls={
        "Documentation": "https://pypi.org/project/pccora/",
        "Source": "https://github.com/kinow/pccora",
        "Tracker": "https://github.com/kinow/pccora/issues"
    }
)
