import requests


class APIError(Exception):
    pass


class APIClient:
    """
    Testrail API client. This is an implementation based on the official python testrail API client:
    http://docs.gurock.com/testrail-api2/bindings-python
    with additional abstractions for certain operations.
    """
    def __init__(self, base_url, username, password):
        self.user = username
        self.password = password
        if not base_url.endswith('/'):
            base_url += '/'
        self.url = base_url + 'index.php?/api/v2/'
        self.session = requests.Session()
        self.session.auth = (self.user, self.password)
        self.session.headers.update({'Content-Type': 'application/json'})

    def send_get(self, uri):
        resp = self.session.get(self.url + uri)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise APIError(e.message + '\n' + str(resp.content))
        else:
            return resp.json()

    def send_post(self, uri, data):
        resp = self.session.post(self.url + uri, json=data)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise APIError(e.message + '\n' + str(resp.content))
        else:
            return resp.json()

    def create_run(self, project_id, suite_id, name):
        return self.send_post('add_run/%s' % project_id,
                              data={
                                  'suite_id': suite_id,
                                  'name': name,
                                  'include_all': True,
                              })

    def get_run_for_branch(self, project_id, branch_name):
        get_runs_endpoint = 'get_runs/{project_id}&is_completed=0'.format(project_id=project_id)
        test_runs = self.send_get(get_runs_endpoint)
        for test_run in test_runs:
            if test_run['name'] == branch_name:
                return test_run
        return None

    def get_cases(self, project_id, suite_id):
        return self.send_get('get_cases/%s&suite_id=%s' % (project_id, suite_id))

    def create_result(self, run_id, case_id, status, comment, elapsed, version=None):
        return self.send_post('add_result_for_case/%s/%s' % (run_id, case_id),
                              data={
                                  'status_id': status,
                                  'comment': comment,
                                  'version': version,
                                  'elapsed': elapsed,
                              })
