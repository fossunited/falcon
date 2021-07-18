"""livecode kernel to execute code in a sandbox.
"""
import aiodocker
from pathlib import Path
import tempfile
import json
from .msgtypes import ExecMessage

KERNEL_SPEC = {
    "python": {
        "image": "python:3.9",
        "command": ["python", "main.py"],
        "code_filename": "main.py"
    },
    "python-canvas": {
        "image": "livecode-python-canvas",
        "command": ["python", "/opt/startup.py"],
        "code_filename": "main.py"
    }
}

class Kernel:
    def __init__(self, runtime):
        self.runtime = runtime

    async def execute(self, msg: ExecMessage):
        """Executes the code and yields the messages whenever something is printed by that code.
        """
        kspec = KERNEL_SPEC[self.runtime]
        code_filename = msg.code_filename or kspec['code_filename']
        with tempfile.TemporaryDirectory() as root:
            self.root = root
            self.save_file(root, code_filename, msg.code)

            for f in msg.files:
                self.save_file(root, f['filename'], f['contents'])

            container = await self.start_container(
                image=kspec['image'],
                command=msg.command or kspec['command'],
                root=root,
                env=msg.env)

            # TODO: read stdout and stderr seperately
            try:
                async for line in self.read_docker_log_lines(container):
                    if line.startswith("--MSG--"):
                        json_message = line[len("--MSG--"):].strip()
                        msg = json.loads(json_message)
                        # ignore bad cases
                        if "msgtype" not in msg:
                            # TODO: print a warning message
                            continue
                    else:
                        msg = dict(msgtype="write", file="stdout", data=line)
                    yield msg
            finally:
                status = await container.wait()
                yield {"msgtype": "exitstatus", "exitstatus": status['StatusCode']}
                await container.delete()

    async def read_docker_log_lines(self, container, max_line_length=1000000):
        """Reads the docker log line by line.

        When a line is longer, the docker api gives the line in chunks.
        This function combines the chunks into a line and returns one
        line at a time as an generator.

        Also includes a protection against very long lines. if a line
        has more than max_line_length (default 1 million), reading
        is aborted and no further data is read.
        """
        logs = container.log(stdout=True, stderr=True, follow=True)

        remaining = ""

        async for line in logs:
            line = remaining + line
            remaining = ""

            if line.endswith("\n"):
                yield line
            else:
                # protection against very large images
                # stop reading further when the line has more than max_line_length
                if len(line) > max_line_length:
                    return
                remaining = line

        if remaining:
            yield remaining

    def save_file(self, root, filename, contents):
        Path(root, filename).write_text(contents)

    async def start_container(self, image, command, root, env):
        docker = aiodocker.Docker()
        print('== starting a container ==')
        command = ["timeout", "10"] + command
        env_entries = [f'{k}={v}' for k, v in env.items()]
        config = {
            'Cmd': command,
            'Image': image,
            'Env': ["PYTHONUNBUFFERED=1", "PYTHONDONTWRITEBYTECODE=1"] + env_entries,
            'HostConfig': {
                'Binds': [
                    root + ":/app"
                ],
                "Memory": 100*1024*1024,
                "CPUQuota": 10000,
                "CPUPeriod": 100000,
            },
            'WorkingDir': '/app',
        }
        container = await docker.containers.create(
            config=config
        )
        await container.start()
        return container
