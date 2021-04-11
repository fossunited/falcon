"""livecode kernel to execute code in a sandbox.
"""
import aiodocker
from pathlib import Path
import tempfile
import json

KERNEL_SPEC = {
    "python": {
        "image": "python:3.9",
        "command": ["python", "main.py"]
    },
    "python-canvas": {
        "image": "livecode-python-canvas",
        "command": ["python", "/opt/startup.py"]
    }
}

class Kernel:
    def __init__(self, runtime):
        self.runtime = runtime

    async def execute(self, code, env):
        """Executes the code and yields the messages whenever something is printed by that code.
        """
        with tempfile.TemporaryDirectory() as root:
            self.root = root
            self.save_file(root, "main.py", code)

            kspec = KERNEL_SPEC[self.runtime]
            container = await self.start_container(kspec['image'], kspec['command'], root)

            # TODO: read stdout and stderr seperately
            try:
                logs = container.log(stdout=True, stderr=True, follow=True)
                #await self.ws.send_json({"msgtype": "debug", "message": "started container\n"})
                async for line in logs:
                    if line.startswith("--DRAW--"):
                        cmd = line[len("--DRAW--"):].strip()
                        msg = dict(msgtype="draw", cmd=json.loads(cmd))
                    else:
                        msg = dict(msgtype="write", file="stdout", data=line)
                    yield msg
            finally:
                status = await container.wait()
                yield {"msgtype": "exitstatus", "exitstatus": status['StatusCode']}
                await container.delete()

    def save_file(self, root, filename, contents):
        Path(root, filename).write_text(contents)

    async def start_container(self, image, command, root):
        docker = aiodocker.Docker()
        print('== starting a container ==')
        config = {
            'Cmd': command,
            'Image': image,
            'Env': ["PYTHONUNBUFFERED=1"],
            'HostConfig': {
                'Binds': [
                    root + ":/app"
                ]
            },
            'WorkingDir': '/app',
        }
        container = await docker.containers.create(
            config=config
        )
        await container.start()
        return container


