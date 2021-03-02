"""livecode kernel to execute code in a sandbox.
"""
import aiodocker
from pathlib import Path
import tempfile

class Kernel:
    def __init__(self, ws, runtime):
        self.ws = ws
        self.runtime = runtime

    async def execute(self, code, env):
        with tempfile.TemporaryDirectory() as root:
            self.root = root
            self.save_file(root, "main.py", code)

            image = "python:3.9"
            command = ["python", "mai2.py"]

            container = await self.start_container(image, command, root)

            # TODO: read stdout and stderr seperately
            try:
                logs = container.log(stdout=True, stderr=True, follow=True)
                await self.ws.send_json({"msgtype": "debug", "message": "started container\n"})
                async for line in logs:
                    await self.ws.send_json({"msgtype": "write", "file": "stdout", "data": line})
            finally:
                status = await container.wait()
                await self.ws.send_json({"msgtype": "exitstatus", "exitstatus": status['StatusCode']})
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


