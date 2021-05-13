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
        print("runexec", data)
        client = TestClient(app)
        response = client.post('/exec', json=data['exec'])
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
