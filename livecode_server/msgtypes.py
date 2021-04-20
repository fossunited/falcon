"""Message types for livecode.
"""

class ExecMessage:
    """Message for executing code.
    """
    def __init__(self, data):
        self.runtime = data['runtime']
        self.code = data['code']
        self.code_filename = data.get('code_filename')
        self.files = data.get('files') or []
        self.env = data.get('env') or {}
        self.command = data.get('command')

