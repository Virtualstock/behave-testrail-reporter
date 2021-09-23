# -*- coding: utf-8 -*-

import unittest
import os
import mock

from behave_testrail_reporter.api import APIClient


class APIClientTestCase(unittest.TestCase):
    def build_mocked_requests_get_response(self, json_data, status_code):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

            def raise_for_status(self):
                """@todo Implement this when you need to test how bad responses are handled."""

        return MockResponse(json_data, status_code)

    def test_env_variables_not_present(self):
        with self.assertRaises(ValueError) as context:
            APIClient(base_url="index.php/")

        expected_message = (
            u"Environment variables to authenticate on Testrail API are not defined!"
        )
        self.assertTrue(expected_message in str(context.exception))

    def test_env_variables_user_not_present(self):
        test_environment = {u"TESTRAIL_USER": u"", u"TESTRAIL_KEY": u"simpson123"}

        with mock.patch.dict(os.environ, test_environment):
            with self.assertRaises(ValueError):
                APIClient(base_url="index.php/")

    def test_env_variables_key_not_present(self):
        test_environment = {
            u"TESTRAIL_USER": u"homer@springfield.test",
            u"TESTRAIL_KEY": u"",
        }

        with mock.patch.dict(os.environ, test_environment):
            with self.assertRaises(ValueError):
                APIClient(base_url="index.php/")

    def test_env_variables_user_and_pass(self):
        test_environment = {
            u"TESTRAIL_USER": u"homer@springfield.test",
            u"TESTRAIL_KEY": u"simpson123",
        }

        with mock.patch.dict(os.environ, test_environment):
            api_client = APIClient(base_url="index.php/")

        self.assertEqual(u"homer@springfield.test", api_client.user)
        self.assertEqual(u"simpson123", api_client.password)

    def test_get_cases(self):
        test_environment = {
            u"TESTRAIL_USER": u"homer@springfield.test",
            u"TESTRAIL_KEY": u"simpson123",
        }
        fake_project_id = 111
        fake_suite_id = 222
        fake_testrail_v2_cases_response_1_json = {
            "offset": 0,
            "limit": 1,
            "size": 1,
            "_links": {
                "next": "/api/v2/get_cases/111&suite_id=222&limit=1&offset=1",
                "prev": None,
            },
            "cases": [
                {
                    "id": 10001,
                    "title": "Manager Login",
                    "section_id": 24776,
                    "template_id": 2,
                    "type_id": 6,
                    "priority_id": 2,
                    "milestone_id": None,
                    "refs": "C22849",
                    "created_by": 37,
                    "created_on": 1531998824,
                    "updated_by": 37,
                    "updated_on": 1568821603,
                    "estimate": None,
                    "estimate_forecast": "3s",
                    "suite_id": 663,
                    "display_order": 2,
                    "is_deleted": 0,
                    "custom_needs_update": False,
                    "custom_bdd_label": 2,
                    "custom_regression": False,
                    "custom_preconds": "Given I am not logged in",
                    "custom_steps": None,
                    "custom_steps_separated": [
                        {
                            "content": "When I click login",
                            "expected": "I can see the login page",
                        },
                        {
                            "content": "Then I enter my username and password for Manager001",
                            "expected": "Populate login form",
                        },
                        {
                            "content": "Then I click 'Login'",
                            "expected": "Navigates to dashboard page",
                        },
                    ],
                    "custom_expected": None,
                    "custom_mission": None,
                    "custom_qa_comments": None,
                }
            ],
        }
        fake_testrail_v2_cases_response_2_json = {
            "offset": 1,
            "limit": 1,
            "size": 1,
            "_links": {"next": None, "prev": None},
            "cases": [
                {
                    "id": 10002,
                    "title": "Manager Logout",
                    "section_id": 24776,
                    "template_id": 2,
                    "type_id": 6,
                    "priority_id": 2,
                    "milestone_id": None,
                    "refs": "C22849",
                    "created_by": 37,
                    "created_on": 1531998824,
                    "updated_by": 37,
                    "updated_on": 1568821603,
                    "estimate": None,
                    "estimate_forecast": "3s",
                    "suite_id": 663,
                    "display_order": 2,
                    "is_deleted": 0,
                    "custom_needs_update": False,
                    "custom_bdd_label": 2,
                    "custom_regression": False,
                    "custom_preconds": "Given I am logged in as a Manager user",
                    "custom_steps": None,
                    "custom_steps_separated": [
                        {
                            "content": "When I click on my name",
                            "expected": "I can see the dropdown menu",
                        },
                        {
                            "content": "Then I click on the 'Sign out' option",
                            "expected": "Navigates to the login screen",
                        },
                    ],
                    "custom_expected": None,
                    "custom_mission": None,
                    "custom_qa_comments": None,
                }
            ],
        }
        expected_number_of_cases = 2
        expected_cases = (
            fake_testrail_v2_cases_response_1_json["cases"]
            + fake_testrail_v2_cases_response_2_json["cases"]
        )

        mock_response_1 = self.build_mocked_requests_get_response(
            json_data=fake_testrail_v2_cases_response_1_json, status_code=200
        )
        mock_response_2 = self.build_mocked_requests_get_response(
            json_data=fake_testrail_v2_cases_response_2_json, status_code=200
        )

        with mock.patch.dict(os.environ, test_environment):
            api_client = APIClient(base_url="https://www.testrail.test")

        with mock.patch(
            "behave_testrail_reporter.api.requests.Session.get"
        ) as request_mock:
            request_mock.side_effect = [mock_response_1, mock_response_2]
            cases = api_client.get_cases(
                project_id=fake_project_id, suite_id=fake_suite_id
            )

        self.assertEqual(expected_number_of_cases, len(cases))
        self.assertEqual(expected_cases, cases)

    def test_get_runs(self):
        test_environment = {
            u"TESTRAIL_USER": u"homer@springfield.test",
            u"TESTRAIL_KEY": u"simpson123",
        }
        fake_project_id = 111

        fake_testrail_v2_runs_response_1_json = {
            "offset": 0,
            "limit": 1,
            "size": 1,
            "_links": {
                "next": "/api/v2/get_runs/111&is_completed=0&name=master&limit=1&offset=1",
                "prev": None,
            },
            "runs": [
                {
                    "id": 1865,
                    "suite_id": 996,
                    "name": "Test run v0.5.0",
                    "description": None,
                    "milestone_id": None,
                    "assignedto_id": 84,
                    "include_all": True,
                    "is_completed": False,
                    "completed_on": None,
                    "config": None,
                    "config_ids": [],
                    "passed_count": 56,
                    "blocked_count": 0,
                    "untested_count": 187,
                    "retest_count": 1,
                    "failed_count": 0,
                    "custom_status1_count": 0,
                    "custom_status2_count": 0,
                    "custom_status3_count": 0,
                    "custom_status4_count": 0,
                    "custom_status5_count": 0,
                    "custom_status6_count": 0,
                    "custom_status7_count": 0,
                    "project_id": 12,
                    "plan_id": None,
                    "created_on": 1632311406,
                    "updated_on": 1632311406,
                    "refs": None,
                    "created_by": 84,
                    "url": "https://custom-domain.testrail.test/index.php?/runs/view/1865",
                }
            ],
        }
        fake_testrail_v2_runs_response_2_json = {
            "offset": 1,
            "limit": 1,
            "size": 1,
            "_links": {"next": None, "prev": None},
            "runs": [
                {
                    "id": 1502,
                    "suite_id": 663,
                    "name": "The Edge for Retail - master",
                    "description": None,
                    "milestone_id": None,
                    "assignedto_id": None,
                    "include_all": True,
                    "is_completed": False,
                    "completed_on": None,
                    "config": None,
                    "config_ids": [],
                    "passed_count": 147,
                    "blocked_count": 0,
                    "untested_count": 3,
                    "retest_count": 0,
                    "failed_count": 0,
                    "custom_status1_count": 0,
                    "custom_status2_count": 0,
                    "custom_status3_count": 0,
                    "custom_status4_count": 0,
                    "custom_status5_count": 0,
                    "custom_status6_count": 0,
                    "custom_status7_count": 0,
                    "project_id": 12,
                    "plan_id": None,
                    "created_on": 1583761764,
                    "updated_on": 1583761764,
                    "refs": None,
                    "created_by": 37,
                    "url": "https://custom-domain.testrail.test/index.php?/runs/view/1502",
                }
            ],
        }
        expected_number_of_test_runs = 2
        expected_test_runs = (
            fake_testrail_v2_runs_response_1_json["runs"]
            + fake_testrail_v2_runs_response_2_json["runs"]
        )

        mock_response_1 = self.build_mocked_requests_get_response(
            json_data=fake_testrail_v2_runs_response_1_json, status_code=200
        )
        mock_response_2 = self.build_mocked_requests_get_response(
            json_data=fake_testrail_v2_runs_response_2_json, status_code=200
        )

        with mock.patch.dict(os.environ, test_environment):
            api_client = APIClient(base_url="https://www.testrail.test")

        with mock.patch(
            "behave_testrail_reporter.api.requests.Session.get"
        ) as request_mock:
            request_mock.side_effect = [mock_response_1, mock_response_2]
            test_runs = api_client.get_test_runs(project_id=fake_project_id)

        self.assertEqual(expected_number_of_test_runs, len(test_runs))
        self.assertEqual(expected_test_runs, test_runs)
