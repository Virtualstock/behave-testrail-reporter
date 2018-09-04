# -*- coding: utf-8 -*-

import unittest
import os

from behave_testrail_reporter.api import APIClient


class APIClientTestCase(unittest.TestCase):
    def setUp(self):
        if os.environ.get(u'TESTRAIL_USER'):
            del os.environ[u'TESTRAIL_USER']
        if os.environ.get(u'TESTRAIL_KEY'):
            del os.environ[u'TESTRAIL_KEY']

    def test_env_variables_not_present(self):
        with self.assertRaises(ValueError) as context:
            APIClient(base_url='index.php/')

        self.assertTrue(
            'Environment variables to authenticate on Testrail API are not defined!' in str(context.exception)
        )

    def test_env_variables_user_not_present(self):
        os.environ[u'TESTRAIL_KEY'] = u'simpson123'

        with self.assertRaises(ValueError):
            APIClient(base_url='index.php/')

    def test_env_variables_key_not_present(self):
        os.environ[u'TESTRAIL_USER'] = u'homer@springfield.test'

        with self.assertRaises(ValueError):
            APIClient(base_url='index.php/')

    def test_env_variables_user_and_pass(self):
        os.environ[u'TESTRAIL_USER'] = u'homer@springfield.test'
        os.environ[u'TESTRAIL_KEY'] = u'simpson123'

        api_client = APIClient(base_url='index.php/')

        self.assertEquals(u'homer@springfield.test', api_client.user)
        self.assertEquals(u'simpson123', api_client.password)
