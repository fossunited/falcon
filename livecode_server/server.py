"""livecode server.
"""
from starlette.applications import Starlette
from starlette.datastructures import UploadFile
from starlette.endpoints import WebSocketEndpoint
from starlette.responses import StreamingResponse, PlainTextResponse
from starlette.routing import Route, WebSocketRoute, Mount
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import json
import time
import shlex

from .kernel import Kernel
from .utils import templates_dir, static_dir, codemirror_dir
from .msgtypes import ExecMessage

templates = Jinja2Templates(directory=templates_dir)

async def home(request):
    return templates.TemplateResponse('index.html', {'request': request})

class LiveCode(WebSocketEndpoint):
    """The websocket endpoint for livecode.
    """
    encoding = 'json'

    async def on_connect(self, ws):
        await ws.accept()
        await ws.send_json({"msgtype": "welcome", "message": "welcome to livecode"})

    async def on_receive(self, ws, msg):
        """This function is called whenever a message is received from the client.
        """
        # TODO: validate the msg
        msgtype = msg.get("msgtype")
        if msgtype == "ping":
            await self.on_ping(ws, msg)
        elif msgtype == "quit":
            await self.on_quit(ws, msg)
        elif msgtype == "exec":
            await self.on_exec(ws, ExecMessage(msg))
        else:
            await self.on_unknown_message(ws, msg)

    async def on_ping(self, ws, msg):
        await ws.send_json({"msgtype": "pong"})

    async def on_quit(self, ws, msg):
        await ws.send_json({"msgtype": "goodbye"})
        await ws.close()

    async def on_exec(self, ws, msg: ExecMessage):
        k = Kernel(msg.runtime)
        async for kmsg in k.execute(msg):
            await ws.send_json(kmsg)
        await ws.close()

    async def on_unknown_message(self, ws, msg):
        msgtype = msg.get("msgtype")
        await ws.send_json({
            "msgtype": "error",
            "error": f"Unknown message type: {msgtype}",
            "msg": msg
        })


def _get_runtime_env(request):
    if 'x-falcon-env' in request.headers:
        value = request.headers['x-falcon-env']
        env = dict(kv.split("=", 1) for kv in value.split())
    else:
        env = {}
    if "x-falcon-mode" in request.headers:
        env['FALCON_MODE'] = request.headers['x-falcon-mode']
    return env

def _get_runtime_args(request):
    args = request.headers.get("X-falcon-args")
    if args:
        return shlex.split(args)
    else:
        return []

async def runtime_exec(request):
    t0 = time.time()
    runtime = request.path_params['runtime']
    env = _get_runtime_env(request)
    args = _get_runtime_args(request)

    if "multipart/form-data" in request.headers['content-type']:
        form = await request.form()
        exec_msg = ExecMessage({
            "runtime": runtime,
            "env": env,
            "code": "",
            "files": [
                {"filename": name, "contents": (await f.read()).decode("utf-8")}
                for name, f in form.items()
                if isinstance(f, UploadFile)],
            "command": args
        })
    else:
        code_bytes = await request.body()
        code = code_bytes.decode('utf-8')
        exec_msg = ExecMessage({
            "runtime": runtime,
            "code": code,
            "env": env,
            "command": args
        })

    k = Kernel(runtime)
    async def process():
        output = []
        exit_status = -1
        async for msg in k.execute(exec_msg):
            if msg['msgtype'] == 'write':
                output.append(msg['data'])
            elif msg['msgtype'] == 'exitstatus':
                exit_status = msg['exitstatus']
        return exit_status, "".join(output)

    exit_status, output = await process()
    t1 = time.time()
    dt = t1-t0
    headers = {
        "X-Falcon-Exit-Status": str(exit_status),
        "X-Falcon-Time-Taken": str(dt)
    }
    return PlainTextResponse(output, media_type="text/plain", headers=headers)

async def livecode_exec(request):
    """Simple API endpoint to execute code and get all the output in the response.
    """
    data = await request.json()
    exec_msg = ExecMessage(data)
    k = Kernel(exec_msg.runtime)

    # When raw_output is set, the JSON is sent directly without filtering
    raw = data.get("raw_output")

    async def process():
        async for msg in k.execute(exec_msg):
            if raw:
                print(msg)
                yield json.dumps(msg) + "\n"
            else:
                if msg['msgtype'] == 'write':
                    yield msg['data']

    return StreamingResponse(process(), media_type='text/plain')

middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'])
]
app = Starlette(
    routes=[
        Route('/', home),
        Route('/exec', livecode_exec, methods=['POST']),
        Route('/runtimes/{runtime}', runtime_exec, methods=['POST']),
        WebSocketRoute("/livecode", LiveCode),
        Mount('/static/codemirror', app=StaticFiles(directory=codemirror_dir), name="codemirror"),
        Mount('/static', app=StaticFiles(directory=static_dir), name="static"),
    ],
    middleware=middleware)
