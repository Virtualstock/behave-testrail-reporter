# -*- coding: utf-8 -*-

import unittest
import os
import mock

from behave_testrail_reporter.api import APIClient


class APIClientTestCase(unittest.TestCase):
    def test_env_variables_not_present(self):
        with self.assertRaises(ValueError) as context:
            APIClient(base_url='index.php/')

        self.assertTrue(
            'Environment variables to authenticate on Testrail API are not defined!' in str(context.exception)
        )

    def test_env_variables_user_not_present(self):
        test_environment = {u'TESTRAIL_USER': u'', u'TESTRAIL_KEY': u'simpson123'}

        with mock.patch.dict(os.environ, test_environment):
            with self.assertRaises(ValueError):
                APIClient(base_url='index.php/')

    def test_env_variables_key_not_present(self):
        test_environment = {u'TESTRAIL_USER': u'homer@springfield.test', u'TESTRAIL_KEY': u'', }

        with mock.patch.dict(os.environ, test_environment):
            with self.assertRaises(ValueError):
                APIClient(base_url='index.php/')

    def test_env_variables_user_and_pass(self):
        test_environment = {u'TESTRAIL_USER': u'homer@springfield.test', u'TESTRAIL_KEY': u'simpson123'}

        with mock.patch.dict(os.environ, test_environment):
            api_client = APIClient(base_url='index.php/')

        self.assertEqual(u'homer@springfield.test', api_client.user)
        self.assertEqual(u'simpson123', api_client.password)
