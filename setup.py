import sys
import os
from setuptools import setup, find_packages

long_description = 'Please see our GitHub README'
if os.path.exists('README.md'):
    long_description = open('README.md').read()

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()


requirements = ['jsonschema', 'behave', 'pyyaml', 'requests']
test_requirements = ['coverage', 'flake8', 'mock']

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
    install_requires=requirements,
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
