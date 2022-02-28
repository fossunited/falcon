def _customize():
    import os
    import sys
    import io
    import json
    import builtins

    FALCON_STDIN = os.getenv("FALCON_STDIN")
    if not FALCON_STDIN:
        return
    try:
        stdin_json = '"' + FALCON_STDIN + '"'
    except ValueError:
        stdin_json = '""'
    stdin_text = json.loads(stdin_json)
    sys.stdin = io.StringIO(stdin_text)

    def _input(prompt=None):
        if prompt:
            print(prompt, end="")
        line = sys.stdin.readline().strip("\n")
        print(line)
        return line
    builtins.input = _input

_customize()
del _customize
