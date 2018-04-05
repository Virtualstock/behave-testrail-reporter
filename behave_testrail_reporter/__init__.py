import re
import os
import yaml
import sys

from behave.reporter.base import Reporter
from behave.model import ScenarioOutline
from behave.model_core import Status

from .api import APIClient

# -- DISABLED: optional_steps = ('untested', 'undefined')
optional_steps = (Status.untested,)  # MAYBE: Status.undefined
status_order = (Status.passed, Status.failed, Status.skipped,
                Status.undefined, Status.untested)


def format_summary(statement_type, summary):
    parts = []
    for status in status_order:
        if status.name not in summary:
            continue
        counts = summary[status.name]
        if status in optional_steps and counts == 0:
            # -- SHOW-ONLY: For relevant counts, suppress: untested items, etc.
            continue

        if not parts:
            # -- FIRST ITEM: Add statement_type to counter.
            label = statement_type
            if counts != 1:
                label += 's'
            part = u'%d %s %s' % (counts, label, status.name)
        else:
            part = u'%d %s' % (counts, status.name)
        parts.append(part)
    return ', '.join(parts)


class TestrailReporter(Reporter):
    STATUS_PASSED = 1
    STATUS_BLOCKED = 2
    STATUS_UNTESTED = 3
    STATUS_RETEST = 4
    STATUS_FAILED = 5
    show_failed_cases = True

    CASE_TAG_PREFIX = 'testrail-C'

    # map Behave to Testrail test result status
    STATUS_MAPS = {
        'passed': STATUS_PASSED,
        'failed': STATUS_FAILED,
        'skipped': STATUS_UNTESTED,
        'undefined': STATUS_UNTESTED,
        'executing': STATUS_UNTESTED,
        'untested': STATUS_UNTESTED,
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
        self.case_summary = {
            Status.passed.name: 0,
            Status.failed.name: 0,
            Status.skipped.name: 0,
            Status.untested.name: 0}
        self.duration = 0.0
        self.failed_cases = []

    def feature(self, feature):
        self.duration += feature.duration
        for scenario in feature:
            if isinstance(scenario, ScenarioOutline):
                self.process_scenario_outline(scenario)
            else:
                self.process_scenario(scenario)

    def end(self):
         # -- SHOW FAILED SCENARIOS (optional):
        if self.show_failed_cases and self.failed_cases:
            print('\nTestrail test results failed for test cases:\n')
            for case_id in self.failed_cases:
                print(u'case_id:  %s\n' % (case_id))
            print('\n')

        # -- SHOW SUMMARY COUNTS:
        print(format_summary('testrail test case', self.case_summary))
        timings = (int(self.duration / 60.0), self.duration % 60)
        print('Took %dm%02.3fs\n' % timings)

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
            raise Exception(
                'Your testrail.yml config file does not have any project configured!')

        for project_config in projects_config:
            testrail_project = TestrailProject(
                id=project_config.get('id'),
                name=project_config.get('name'),
                suite_id=project_config.get('suite_id'),
                allowed_branch_pattern=project_config.get(
                    'allowed_branch_pattern')
            )
            self.projects.append(testrail_project)

    def _can_generate_test_run_for_branch(self, testrail_project, branch_name):
        """
        This method contains the logic to decide if the branch_name is allowed to have test run and
        test results added to it.
        """
        allowed_branch_names = r'' + \
            str(testrail_project.allowed_branch_pattern)

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
        for tag in scenario.tags + scenario.feature.tags:
            if tag.startswith(TestrailReporter.CASE_TAG_PREFIX):
                case_id = tag[len(TestrailReporter.CASE_TAG_PREFIX):]
                # loop through all projects to ensure if test exists on both projects it is pushed
                for testrail_project in self.projects:
                    if case_id in testrail_project.cases:
                        comment = '{}\n'.format(scenario.name)
                        comment += '\n'.join(
                            ['->  {} {} [{}]'.format(step.keyword, step.name, step.status) for step in scenario.steps])

                        testrail_status = TestrailReporter.STATUS_MAPS[scenario.status]

                        # When adding a test result untested status is not allowed status
                        # @see http://docs.gurock.com/testrail-api2/reference-results#add_result
                        if testrail_status is self.STATUS_UNTESTED:
                            self.case_summary[Status.skipped.name] += 1
                            continue

                        if not self._can_generate_test_run_for_branch(testrail_project, self.branch_name):
                            self.case_summary[Status.skipped.name] += 1
                            continue

                        was_test_result_added = self.testrail_client.create_result(
                            testrail_project.test_run['id'],
                            case_id,
                            status=testrail_status,
                            comment=comment,
                            elapsed='%ds' % int(scenario.duration)
                        )

                        if was_test_result_added:
                            self.case_summary[Status.passed.name] += 1
                        else:
                            self.failed_cases.append(case_id)
                    else:
                        self.case_summary[Status.untested.name] += 1

    def process_scenario_outline(self, scenario_outline):
        for scenario in scenario_outline.scenarios:
            self.process_scenario(scenario)


class TestrailProject(object):
    def __init__(self, id, name, suite_id, test_run_name='', allowed_branch_pattern='*'):
        self.id = id
        self.name = name
        self.suite_id = suite_id
        self.test_run_name = test_run_name
        self.allowed_branch_pattern = allowed_branch_pattern
        self.test_run = None
        self.cases = {}
