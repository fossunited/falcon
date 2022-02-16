"""
Driver for py.test tests.

Run the py.test with junitxml, parses the output of junitxml and returns it as json.
"""
import sys
import subprocess
from xml.dom import minidom
import json

class TestResultParser:
    def parse_file(self, filename):
        return self.parse(open(filename).read())

    def parse(self, xmltext):
        doc = minidom.parseString(xmltext)
        root = doc.documentElement
        test_suites = [self.process_testsuite(e) for e in root.childNodes]
        suite = test_suites[0]
        testcases = suite['testcases']
        stats = {
            "tests": suite.get('tests', '-'),
            "passed": sum(1 for t in testcases if t['outcome'] == 'passed'),
            "failed": sum(1 for t in testcases if t['outcome'] == 'failed'),
            "time_taken": suite.get('time')
        }
        return {
            "testcases": testcases,
            "stats": stats
        }

    def process_testsuite(self, e):
        d =  self.get_attrs(e)
        nodes = e.getElementsByTagName("testcase")
        d['testcases'] =[self.process_testcase(node) for node in nodes]
        return d

    def process_testcase(self, e):
        d =  self.get_attrs(e)
        filename = d['classname'] + ".py"
        name = d['name']
        time_taken = d['time']
        outcome = "passed"
        d = {
            "filename": filename,
            "name": name,
            "time_taken": time_taken,
            "outcome": outcome
        }

        nodes = e.getElementsByTagName("failure")
        if nodes:
            d['outcome'] = "failed"
            d.update(self.process_failure(nodes[0]))
        return d

    def get_attrs(self, e):
        return {k: a.value for k, a in dict(e.attributes).items()}

    def get_text(self, e):
        rc = []
        for node in e.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def process_failure(self, e):
        return {
            "error_message": e.getAttribute("message"),
            "error_detail": self.get_text(e)
        }

cmd = "py.test -p no:cacheprovider --junitxml /tmp/pytest.xml".split()

p = subprocess.run(cmd, capture_output=True)
d = TestResultParser().parse_file("/tmp/pytest.xml")
print(json.dumps(d, indent=True))
sys.exit(p.returncode)
