import re
import os
import yaml
import sys

import behave
from behave.reporter.base import Reporter
from .api import APIClient


class TestrailReporter(Reporter):
    STATUS_PASSED = 1
    STATUS_BLOCKED = 2
    STATUS_UNTESTED = 3
    STATUS_RETEST = 4
    STATUS_FAILED = 5

    CASE_TAG_PREFIX = 'testrail-C'

    STATUS_MAPS = {
        'passed': STATUS_PASSED,
        'failed': STATUS_FAILED,
        'skipped': STATUS_UNTESTED,
    }

    def __init__(self, branch_name):
        self.config = {}
        self.projects = []
        self.username = os.environ.get('TESTRAIL_USER')
        self.secret_key = os.environ.get('TESTRAIL_KEY')
        # @todo ensure username and secret_key are set
        # @todo ensure project_id and suite_id are set
        self.branch_name = branch_name
        self.testrail_client = None
        self.testrail_run = None
        self.testrail_cases = {}
        self._load_config()
        self.setup_test_run()

    def feature(self, feature):
        for scenario in feature.scenarios:
            self.process_scenario(scenario)

    def end(self):
        print('---end of tests being called from reporter--')
        # @todo print report of what happened in this reporter, e.g. the number os tests pushed to testrail successfully

    def _load_config(self):
        with open('testrail.yml', 'r') as stream:
            try:
                self.config = yaml.load(stream)
                self._load_projects_from_config(self.config)
            except yaml.YAMLError as exc:
                print(exc)

    def _load_projects_from_config(self, config):
        projects_config = config.get('projects', [])
        if len(projects_config) is 0:
            raise Exception('Your testrail.yml config file does not have any project configured!')

        for project_config in projects_config:
            testrail_project = TestrailProject(
                id=project_config.get('id'),
                name=project_config.get('name'),
                suite_id=project_config.get('suite_id'),
                allowed_branch_pattern=project_config.get('suite_id')
            )
            self.projects.append(testrail_project)

    def _can_generate_test_run_for_branch(self, project, branch_name):
        """
        This method contains the logic to decide if the branch_name is allowed to have test run and
        test results added to it.
        """
        allowed_branch_names = r'' + str(project.allowed_branch_pattern)

        return bool(re.match(allowed_branch_names, branch_name))

    def setup_test_run(self):
        """
        Sets up the testrail run.
        """
        self.testrail_client = APIClient(
            base_url=self.config.get('base_url'),
            username=self.username,
            password=self.secret_key,
        )

        for testrail_project in self.projects:
            testrail_project.test_run = self.testrail_client.get_run_for_branch(
                testrail_project.id,
                self.branch_name
            )

            if testrail_project.test_run is None:
                # @todo allow to customise the test run name that is created
                test_run_name = self.branch_name
                testrail_project.test_run = self.testrail_client.create_run(
                    testrail_project.id,
                    testrail_project.suite_id,
                    test_run_name,
                )

            cases = self.testrail_client.get_cases(
                testrail_project.id,
                testrail_project.suite_id,
            )
            testrail_project.cases = {str(case['id']): case for case in cases}

    def process_scenario(self, scenario):
        """
        Reports the test results for the given scenario to the testrail run.
        """
        pass
        for tag in scenario.tags + scenario.feature.tags:
            if tag.startswith(TestrailReporter.CASE_TAG_PREFIX):
                case_id = tag[len(TestrailReporter.CASE_TAG_PREFIX):]
                # loop through all projects to ensure if test exists on both projects it is pushed
                for testrail_project in self.projects:
                    if case_id in testrail_project.cases:
                        comment = '{}\n'.format(scenario.name)
                        comment += '\n'.join(
                            ['->  {} {} [{}]'.format(step.keyword, step.name, step.status) for step in scenario.steps])
                        status = TestrailReporter.STATUS_MAPS[scenario.status]
                        # When adding a test result untested status is not allowed status
                        # @see http://docs.gurock.com/testrail-api2/reference-results#add_result
                        if status is self.STATUS_UNTESTED:
                            # @todo add this scenario as skipped for reporting purposes
                            continue

                        if not self._can_generate_test_run_for_branch(testrail_project, self.branch_name):
                            # @todo add this case as not pushed because it does not have a valid branch name
                            continue

                        was_test_result_added = self.testrail_client.create_result(
                            testrail_project.test_run['id'],
                            case_id,
                            status=status,
                            comment=comment,
                            elapsed='%ds' % int(scenario.duration)
                        )

                        if was_test_result_added:
                            # @todo add this case_id as pushed successfully to testrail
                            print('test result added succesfully for test case:', case_id)



class TestrailProject(object):
    def __init__(self, id, name, suite_id, test_run_name='', allowed_branch_pattern='*'):
        self.id = id
        self.name = name
        self.suite_id = suite_id
        self.test_run_name = test_run_name
        self.allowed_branch_pattern = allowed_branch_pattern
        self.test_run = None
        self.cases = {}

