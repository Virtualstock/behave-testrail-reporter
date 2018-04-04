# Behave to TestRail Integration

This integration is used to add test results to TestRail automatically when Behave tests are executed.

@todo abstract this into a generic package that can be open sourced and moved out of our codebase.


## Setup

Add `TestrailReporter` to behave reporters in your `/features/environment.py` by adding this code in `before_all()`

```python
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
    name: 'Project Name'
    id: 123
    suite_id: 123
    test_run_name: '{branch_name}'
    allowed_branch_pattern: '^(master|release\/\d+([\.\d]+)?)$'
```

| yaml key               | Description                                                |
| ---------------------- | ---------------------------------------------------------- |
| name                   | Project name                                               |  
| id                     | Testrail project id                                        |  
| suite_id               | Testrail Suite id                                          |  
| test_run_name          | test run name that will be created on testrail             |  
| allowed_branch_pattern | Regular expression to restrict when a test run is executed |  


**Environment variables required**

| Variable name       | Description                 |
| ------------------- | --------------------------- |
| TESTRAIL_KEY        | TestRail user password      |
| TESTRAIL_PROJECT_ID | TestRail project ID         |
| TESTRAIL_SUITE_ID   | TestRail Suite of tests ID  |
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
