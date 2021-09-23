import sys
import os
from setuptools import setup, find_packages

long_description = "Please see our GitHub README"
if os.path.exists("README.md"):
    long_description = open("README.md").read()

REQUIREMENTS = ["jsonschema", "behave", "pyyaml", "requests"]
TEST_REQUIREMENTS = ["coverage", "flake8", "mock", "twine", "codacy-coverage"]

setup(
    name="behave-testrail-reporter",
    version="0.5.1",
    author="Virtualstock",
    author_email="development.team@virtualstock.co.uk",
    url="https://github.com/virtualstock/behave-testrail-reporter/",
    packages=find_packages(exclude=["temp*.py", "register.py", "test"]),
    include_package_data=True,
    license="MIT",
    description="Behave library to integrate with Testrail API",
    keywords=["Behave", "Testrail", "API", "Test", "BDD"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=REQUIREMENTS,
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    test_suite="test",
    tests_require=TEST_REQUIREMENTS,
)
