# -*- coding: utf-8 -*-
import os
import textwrap

import requests


class APIError(Exception):
    pass


class APIClient:
    """
    Testrail API client. This is an implementation based on the official python testrail API client:
    http://docs.gurock.com/testrail-api2/bindings-python
    with additional abstractions for certain operations.
    """

    def __init__(self, base_url):
        self.user = os.environ.get(u"TESTRAIL_USER")
        self.password = os.environ.get(u"TESTRAIL_KEY")

        if not base_url.endswith(u"/"):
            base_url += u"/"
        self.url = base_url + u"index.php?/api/v2/"
        self.session = requests.Session()
        self.session.auth = (self.user, self.password)
        self.session.headers.update({u"Content-Type": u"application/json"})

        if not self.user or not self.password:
            raise ValueError(
                u"Environment variables to authenticate on Testrail API are not defined!\n"
                u"Please define those environment variables: \n"
                u"TESTRAIL_USER and TESTRAIL_KEY"
            )

    def _build_endpoint_from_uri(self, uri):
        return u"{base_url}{uri}".format(base_url=self.url, uri=uri)

    def send_get(self, uri):
        endpoint = self._build_endpoint_from_uri(uri)
        response = self.session.get(endpoint)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            try:
                exception_message = e.message
            except AttributeError:
                exception_message = str(e)
            error_template = textwrap.dedent(
                u"""\
                    Error ({error}) during GET to endpoint: ({endpoint})
                    Response Content: {response_content}
                """
            )
            error_message = error_template.format(
                error=exception_message, endpoint=uri, response_content=response.content
            )
            raise APIError(error_message)
        else:
            return response.json()

    def send_post(self, uri, data):
        endpoint = self._build_endpoint_from_uri(uri)
        response = self.session.post(endpoint, json=data)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            try:
                exception_message = e.message
            except AttributeError:
                exception_message = str(e)
            error_template = textwrap.dedent(
                u"""\
                    Error ({error}) during POST to endpoint: ({endpoint})
                    With data: {data}
                    Response Content: {response_content}
                """
            )
            error_message = error_template.format(
                error=exception_message,
                endpoint=uri,
                data=data,
                response_content=response.content,
            )

            raise APIError(error_message)
        else:
            return response.json()

    def create_run(self, project_id, suite_id, test_run_name):
        uri_create_test_run = u"add_run/{}".format(project_id)
        post_data = {
            u"suite_id": suite_id,
            u"name": test_run_name,
            u"include_all": True,
        }

        return self.send_post(uri=uri_create_test_run, data=post_data)

    def get_test_run_by_project_and_name(self, project_id, test_run_name):
        test_runs = self.get_test_runs(project_id)

        for test_run in test_runs:
            if test_run[u"name"] == test_run_name:
                return test_run
        return None

    def _build_incomplete_test_runs_endpoint(self, project_id, offset):
        return u"get_runs/{project_id}&is_completed=0&offset={offset}".format(
            project_id=project_id, offset=offset
        )

    def get_test_runs(self, project_id, fetched_test_runs=[], offset=0):
        uri_get_project_test_runs = self._build_incomplete_test_runs_endpoint(
            project_id, offset
        )

        api_response = self.send_get(uri=uri_get_project_test_runs)

        test_runs = fetched_test_runs + api_response["runs"]

        if api_response["_links"]["next"]:
            next_offset = offset + api_response["limit"]
            test_runs = self.get_test_runs(
                project_id, fetched_test_runs=test_runs, offset=next_offset
            )

        return test_runs

    def _build_get_cases_endpoint(self, project_id, suite_id, offset=0):
        return u"get_cases/{project}&suite_id={suite}&offset={offset}".format(
            project=project_id, suite=suite_id, offset=offset
        )

    def get_cases(self, project_id, suite_id, fetched_cases=[], offset=0):
        """This will recursively fetch cases from Testrail API until there are no more pages to fetch."""
        uri_get_project_cases = self._build_get_cases_endpoint(
            project_id, suite_id, offset=offset
        )
        api_response = self.send_get(uri=uri_get_project_cases)

        cases = fetched_cases + api_response["cases"]

        if api_response["_links"]["next"]:
            next_offset = offset + api_response["limit"]
            cases = self.get_cases(
                project_id, suite_id, fetched_cases=cases, offset=next_offset
            )

        return cases

    def create_result(self, run_id, case_id, status, comment, elapsed, version=None):
        uri_add_test_result = u"add_result_for_case/{run}/{test_case}".format(
            run=run_id, test_case=case_id
        )
        post_data = {
            u"status_id": status,
            u"comment": comment,
            u"version": version,
            u"elapsed": elapsed,
        }

        return self.send_post(uri=uri_add_test_result, data=post_data)
