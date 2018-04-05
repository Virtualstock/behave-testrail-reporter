import sys
import os
from setuptools import setup, find_packages

long_description = 'Please see our GitHub README'
if os.path.exists('README.md'):
    long_description = open('README.md').read()

test_requirements = []


def getRequires():
    deps = ['jsonschema', 'behave']
    if sys.version_info < (2, 7):
        deps.append('unittest2')
    elif (3, 0) <= sys.version_info < (3, 2):
        deps.append('unittest2py3k')
    return deps


setup(
    name='behave-testrail-reporter',
    version='0.0.1',
    author='Virtualstock',
    author_email='development.team@virtualstock.co.uk',
    url='https://github.com/virtualstock/behave-testrail-reporter/',
    packages=find_packages(exclude=['temp*.py', 'register.py', 'test']),
    include_package_data=True,
    license='MIT',
    description='Behave library to integrate with Testrail API',
    keywords=['Behave', 'Testrail', 'API', 'Test', 'BDD'],
    long_description=long_description,
    install_requires=getRequires(),
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='test',
    tests_require=test_requirements
)
