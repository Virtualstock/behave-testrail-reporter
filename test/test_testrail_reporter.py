import unittest
import sys
import yaml
import os

from behave_testrail_reporter.api import APIClient
from behave_testrail_reporter import TestrailReporter


class TestrailReporterTestCase(unittest.TestCase):
    def setUp(self):
        data = dict(
            base_url='https://test.testrail.net',
            projects=[
                dict(
                    name='Testrail project name',
                    id=1,
                    suite_id=11,
                    allowed_branch_pattern='*',
                ),
                dict(
                    name='Testrail project name',
                    id=2,
                    suite_id=22,
                    allowed_branch_pattern='*',
                )
            ]
        )

        with open('testrail.yml', 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

    def tearDown(self):
        os.remove('testrail.yml')

    def test_load_config(self):
        TestrailReporter('master')
