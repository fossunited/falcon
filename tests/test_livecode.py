"""
LiveCode tests are written as YAML files.

See tests/sessions/*.yml
"""
from pathlib import Path
import pytest
import yaml
import os
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
        self.name = path
        self.steps = yaml.safe_load(open(path))

    def runtest(self):
        client = TestClient(app)
        with client.websocket_connect('/livecode') as ws:
            for step in self.steps:
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

def read_tests_files(path):
    tests = []
    root = Path(__file__).parent
    p = root.joinpath(path)
    files = p.rglob('*.yml')
    return [str(f.relative_to(root)) for f in files]

# Get all tests
testfiles = read_tests_files("sessions")

@pytest.mark.parametrize('filename', testfiles)
def test_fileformats(filename):
    path = Path(__file__).parent.joinpath(filename)
    t = LiveCodeTest(str(path))
    t.runtest()
