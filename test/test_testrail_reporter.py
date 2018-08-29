# -*- coding: utf-8 -*-

import unittest
import sys
import yaml
import os
from functools import partial

from mock import Mock, mock
from behave.model import Scenario, Feature, Status

from behave_testrail_reporter.api import APIClient
from behave_testrail_reporter import TestrailReporter, TestrailProject


class TestrailReporterTestCase(unittest.TestCase):
    def setUp(self):
        data = {
            'base_url': 'https://test.testrail.net',
            'projects': [
                {
                    'name': 'Testrail project name',
                    'id': 1,
                    'suite_id': 11,
                    'allowed_branch_pattern': '.*',
                },
                {
                    'name': 'Testrail project name',
                    'id': 2,
                    'suite_id': 22,
                    'allowed_branch_pattern': '.*',
                }
            ]
        }

        with open(u'testrail.yml', u'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

    def tearDown(self):
        os.remove(u'testrail.yml')

    def test_load_config(self):
        testrail_reporter = TestrailReporter(u'master')
        empty_config = {}

        self.assertNotEqual(empty_config, testrail_reporter.config)

    def test_build_comment_for_scenario(self):
        testrail_reporter = TestrailReporter(u'master')

        step_01 = Mock(status=u'passed', keyword=u'given')
        step_01.name = u'step_01'
        step_02 = Mock(status=u'passed', keyword=u'given')
        step_02.name = u'step_02'

        steps = [step_01, step_02, ]

        mock_scenario = Mock(Scenario)
        mock_scenario.name = u'Dummy scenario'
        mock_scenario.steps = steps
        comment = testrail_reporter._buid_comment_for_scenario(mock_scenario)
        expected_comment = (
            u'Dummy scenario\n'
            u'->  given step_01 [passed]\n'
            u'->  given step_02 [passed]')
        self.assertEqual(expected_comment, comment)

    def test_build_comment_for_scenario_with_utf8_string(self):
        testrail_reporter = TestrailReporter(u'master')

        step_01 = Mock(status=u'passed', keyword=u'given')
        step_01.name = u'step_01 £'

        steps = [step_01]

        mock_scenario = Mock(Scenario)
        mock_scenario.name = u'Dummy scenario'
        mock_scenario.steps = steps
        comment = testrail_reporter._buid_comment_for_scenario(mock_scenario)
        expected_comment = (
            u'Dummy scenario\n'
            u'->  given step_01 £ [passed]')
        self.assertEqual(expected_comment, comment)

    def test_format_duration(self):
        testrail_reporter = TestrailReporter(u'master')
        duration = 69
        formatted_duration = testrail_reporter._format_duration(duration)

        self.assertEquals(u'69s', formatted_duration)

    def test_format_duration_return_one_for_zero_durations(self):
        testrail_reporter = TestrailReporter(u'master')
        duration = 0
        formatted_duration = testrail_reporter._format_duration(duration)

        self.assertEquals(u'1s', formatted_duration)

    @mock.patch('behave_testrail_reporter.TestrailReporter._add_test_result')
    @mock.patch('behave_testrail_reporter.api.APIClient.send_post')
    @mock.patch('behave_testrail_reporter.TestrailReporter._load_test_cases_for_project')
    def test_process_scenario(self, mock_load_test_cases, mocked_post, add_test_result_mock):
        """
            Test to ensure the data that we send to add_test_result is correct.
        """
        testrail_reporter = TestrailReporter(u'master')
        testrail_reporter.projects[0].cases = ['1104']

        step_01 = Mock(status=u'passed', keyword=u'given')
        step_01.name = u'step_01 £'
        steps = [step_01]

        mock_feature = Mock(Feature)
        mock_feature.tags = []

        mock_scenario = Mock(Scenario)
        mock_scenario.tags = [u'testrail-C1104']
        mock_scenario.name = u'Dummy scenario'
        mock_scenario.steps = steps
        mock_scenario.feature = mock_feature
        mock_scenario.status = Status.passed

        add_test_result_mock.return_value = {}
        mocked_post.return_value = Mock(ok=True)
        comment = testrail_reporter._buid_comment_for_scenario(mock_scenario)

        testrail_reporter.process_scenario(mock_scenario)

        add_test_result_mock.assert_called_with(
            project=testrail_reporter.projects[0],
            case_id=u'1104',
            status=1,
            comment=comment,
            elapsed_seconds=mock_scenario.duration,
        )

    def test_status_map_passed(self):
        expected_status = TestrailReporter.STATUS_MAPS[u'passed']
        self.assertEquals(expected_status, TestrailReporter.STATUS_MAPS[Status.passed.name])

    def test_status_map_failed(self):
        expected_status = TestrailReporter.STATUS_MAPS[u'failed']
        self.assertEquals(expected_status, TestrailReporter.STATUS_MAPS[Status.failed.name])

    def test_status_map_skipped(self):
        expected_status = TestrailReporter.STATUS_MAPS[u'skipped']
        self.assertEquals(expected_status, TestrailReporter.STATUS_MAPS[Status.skipped.name])

    def test_status_map_undefined(self):
        expected_status = TestrailReporter.STATUS_MAPS[u'undefined']
        self.assertEquals(expected_status, TestrailReporter.STATUS_MAPS[Status.undefined.name])

    def test_status_map_executing(self):
        expected_status = TestrailReporter.STATUS_MAPS[u'executing']
        self.assertEquals(expected_status, TestrailReporter.STATUS_MAPS[Status.executing.name])

    def test_status_map_untested(self):
        expected_status = TestrailReporter.STATUS_MAPS[u'untested']
        self.assertEquals(expected_status, TestrailReporter.STATUS_MAPS[Status.untested.name])


class TestrailReporterTestLoadConfig(unittest.TestCase):
    def test_config_file_is_not_present(self):
        with self.assertRaises(Exception) as context:
            TestrailReporter(u'master')

        exception_message = u'Could not read `testrail.yml` file, check the file exists in root of your project.'
        self.assertTrue(exception_message in context.exception.args[0])

    def test_config_file_is_not_valid_yaml_file(self):
        self.addCleanup(partial(os.remove, u'testrail.yml'))
        with open(u'testrail.yml', 'w') as outfile:
            outfile.write(u'-\n--\n---')

        with self.assertRaises(Exception) as context:
            TestrailReporter(u'master')

        exception_message = u'Error loading testrail.yml file:'
        self.assertTrue(exception_message in context.exception.args[0])

    def test_config_file_is_missing_base_url(self):
        self.addCleanup(partial(os.remove, u'testrail.yml'))
        data = {
            'projects': [
                {
                    'name': 'Testrail project name',
                    'id': 1,
                    'suite_id': 11,
                    'allowed_branch_pattern': '*',
                },
            ]
        }

        with open(u'testrail.yml', u'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

        with self.assertRaises(Exception) as context:
            TestrailReporter(u'master')

        exception_message = u'Invalid testrail.yml file! error: \'base_url\' is a required property'
        self.assertEquals(exception_message, context.exception.args[0])

    def test_config_file_without_projects(self):
        self.addCleanup(partial(os.remove, u'testrail.yml'))
        data = {
            'base_url': 'https://test.testrail.net',
            'projects': []
        }

        with open(u'testrail.yml', u'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

        with self.assertRaises(Exception) as context:
            TestrailReporter(u'master')

        exception_message = u'Your testrail.yml config file does not have any project configured!'
        self.assertEquals(exception_message, context.exception.args[0])


class TestrailProjectTestCase(unittest.TestCase):
    def test_get_test_run_name_default(self):
        project = TestrailProject(1, u'master', 3)
        test_run_name = project.get_test_run_name(branch_name=u'master')

        self.assertEquals(u'master', test_run_name)

    def test_get_test_run_name_branch(self):
        project = TestrailProject(1, u'My Test Suite {branch}', 3, u'')
        test_run_name = project.get_test_run_name(branch_name=u'master')

        self.assertEquals(u'My Test Suite master', test_run_name)

    def test_get_test_run_name_project_id(self):
        project = TestrailProject(1, u'My Test Suite {project_id}', 3)
        test_run_name = project.get_test_run_name(branch_name=u'master')

        self.assertEquals(u'My Test Suite 1', test_run_name)

    def test_get_test_run_name_suite_id(self):
        project = TestrailProject(1, u'My Test Suite {suite_id}', 3)
        test_run_name = project.get_test_run_name(branch_name=u'master')

        self.assertEquals(u'My Test Suite 3', test_run_name)

    def test_get_test_run_name_combined_vars(self):
        project = TestrailProject(1, u'My Test Suite {branch} {project_id} {suite_id}', 3)
        test_run_name = project.get_test_run_name(branch_name=u'master')

        self.assertEquals(u'My Test Suite master 1 3', test_run_name)
