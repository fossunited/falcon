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
                logs = container.log(stdout=True, stderr=True, follow=True)
                #await self.ws.send_json({"msgtype": "debug", "message": "started container\n"})
                async for line in logs:
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

    def save_file(self, root, filename, contents):
        Path(root, filename).write_text(contents)

    async def start_container(self, image, command, root, env):
        docker = aiodocker.Docker()
        print('== starting a container ==')
        env_entries = [f'{k}={v}' for k, v in env.items()]
        config = {
            'Cmd': command,
            'Image': image,
            'Env': ["PYTHONUNBUFFERED=1"] + env_entries,
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


