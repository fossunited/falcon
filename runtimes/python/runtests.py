import sys
import subprocess

cmd = "py.test -p no:cacheprovider --junitxml /tmp/pytest.xml".split()

p = subprocess.run(cmd, capture_output=True)

print(open("/tmp/pytest.xml").read())
