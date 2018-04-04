import unittest
# from . import TestrailResultsReporter
import sys

print(sys.path)
from api import APIClient
from behave_testrail import TestrailResultsReporter


class TestTestrailResultReporter(unittest.TestCase):
    def test_example(self):
        assert True is True

    def test_load_config(self):
        reporter = TestrailResultsReporter()