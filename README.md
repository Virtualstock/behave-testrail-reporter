# Behave to TestRail Reporter


[![CircleCI](https://circleci.com/gh/Virtualstock/behave-testrail-reporter.svg?style=svg)](https://circleci.com/gh/Virtualstock/behave-testrail-reporter)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/469f2b5c86974f4c8147b0fabbd25c34)](https://www.codacy.com/app/BernardoSilva/behave-testrail-reporter?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=VirtualStock/behave-testrail-reporter&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/469f2b5c86974f4c8147b0fabbd25c34)](https://www.codacy.com/app/BernardoSilva/behave-testrail-reporter?utm_source=github.com&utm_medium=referral&utm_content=VirtualStock/behave-testrail-reporter&utm_campaign=Badge_Coverage)

This integration is used to add test results to TestRail automatically when Behave tests are executed.


Example of the generated report:

```
3 testrail test cases passed, 0 failed, 19 skipped, 2 untested
Took 0m6.349s
```

## Install

Can install it using pipenv

```
$ pipenv install behave-testrail-reporter
```

or using pip

```
$ pip install behave-testrail-reporter
```

## Setup

Add `TestrailReporter` to behave reporters in your `/features/environment.py` by adding this code in `before_all()`

```python
from behave_testrail_reporter import TestrailReporter

def before_all(context):
    # ... all your other awesome code in here
    current_branch = os.environ.get('CIRCLE_BRANCH') # Change this to get the current build branch of your CI system
    testrail_reporter = TestrailReporter(current_branch)
    context.config.reporters.append(testrail_reporter)
```


Create a `testrail.yml` config file in the root of your project


Example structure:


```yaml
projects:
  -
    name: 'Test run {branch}'
    id: 123
    suite_id: 456
    allowed_branch_pattern: '^(master|release\/\d+([\.\d]+)?)$'
```

| yaml key               | Description                                                |
| ---------------------- | ---------------------------------------------------------- |
| name                   | Project name                                               |  
| id                     | Testrail project id                                        |  
| suite_id               | Testrail Suite id                                          |  
| allowed_branch_pattern | Regular expression to restrict when a test run is executed |  

**name** - You can use some project variables to create dynamic test run names

| Variable     | Example                 | Result          |
| ------------ | ----------------------- | --------------- |
| {project_id} | 'Test run {project_id}' | Test run 123    |
| {suite_id}   | 'Test run {suite_id}'   | Test run 456    |
| {branch}     | 'Test run {branch}'     | Test run master |


**Environment variables required**

| Variable name       | Description                 |
| ------------------- | --------------------------- |
| TESTRAIL_KEY        | TestRail user password      |
| TESTRAIL_USER       | TestRail user email address |



## How to use

To get test cases marked as success or fail on TestRail we have to add tags with TestRail test case ID
on each scenario.

Test case tag structure:

`prefix` + `test case id`

`@testrail-` + `C1104`

See example below:

```gherkin
Feature: Log in and out

    Background:
        Given I am logged out from Hub
        And I navigate to the home page

    @testrail-C1104
    @testrail-C45933
    Scenario: Admin can login
        When I enter the username admin
        And I enter the password admin
        And I click the Login button
        Then I see the admin's landing page
```

Note: some scenarios can cover multiple TestRail cases, for that you just need to add multiple tags.

## How to run tests

```
tox
```

## How to distribute

If you need to publish a new version of this package you can use this command:

```
python setup.py sdist bdist_wheel
twine upload dist/*
```


# License
Licensed under `MIT license`. View [license](LICENSE).
