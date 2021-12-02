"""
LiveCode tests are written as YAML files.

See tests/sessions/*.yml
"""
from pathlib import Path
import pytest
import yaml
import asyncio
from starlette.testclient import TestClient
from livecode_server.server import app

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

class LiveCodeTest:
    """LiveCodeTest runs all the steps specified in an YAML test file.
    """
    def __init__(self, path):
        self.path = path

    def runtest(self):
        steps = yaml.safe_load(open(self.path))
        client = TestClient(app)
        with client.websocket_connect('/livecode') as ws:
            for step in steps:
                if 'send' in step:
                    # send the message
                    data = step['send']
                    print("send", data)
                    ws.send_json(data)
                elif 'recv' in step:
                    # ensure the received message is matching what is specified
                    expected = step['recv']
                    print("recv", expected)
                    data = ws.receive_json()
                    assert data == expected

    def runexec(self):
        data = yaml.safe_load(open(self.path))
        client = TestClient(app)
        response = client.post('/exec', json=data['exec'])
        assert response.status_code == 200
        assert response.text == data['expected_output']

    def runtime_exec(self):
        data = yaml.safe_load(open(self.path))
        client = TestClient(app)
        path = '/runtimes/' + data['runtime']
        headers = {}
        args = {"headers": headers}
        if 'code' in data:
            args['data'] = data['code']
            headers['content-type'] = "text/plain"
        elif 'files' in data:
            args['files'] = [(f['filename'], f['contents']) for f in data['files']]

        if "env" in data:
            headers['X-FALCON-ENV'] = " ".join(f"{k}={v}" for k, v in data['env'].items())

        if "args" in data:
            headers['X-FALCON-ARGS'] = " ".join(data['args'])

        response = client.post(path, **args)
        assert response.status_code == 200
        assert response.text == data['expected_output']

def read_tests_files(path):
    root = Path(__file__).parent
    p = root.joinpath(path)
    files = p.rglob('*.yml')
    return [str(f.relative_to(root)) for f in files]

# Get all tests
testfiles = read_tests_files("sessions")

@pytest.mark.parametrize('filename', testfiles)
def test_sessions(filename):
    path = Path(__file__).parent.joinpath(filename)
    t = LiveCodeTest(str(path))
    t.runtest()

execfiles = read_tests_files("exec")

@pytest.mark.parametrize('filename', execfiles)
def test_exec(filename):
    path = Path(__file__).parent.joinpath(filename)
    t = LiveCodeTest(str(path))
    t.runexec()


runtime_files = read_tests_files("runtimes")

@pytest.mark.parametrize('filename', runtime_files)
def test_exec(filename):
    path = Path(__file__).parent.joinpath(filename)
    t = LiveCodeTest(str(path))
    t.runtime_exec()
