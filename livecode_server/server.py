"""livecode server.
"""
from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route, WebSocketRoute, Mount
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from .kernel import Kernel
from .utils import templates_dir, static_dir
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

async def livecode_exec(request):
    """Simple API endpoint to execute code and get all the output in the response.
    """
    data = await request.json()
    exec_msg = ExecMessage(data)
    k = Kernel(exec_msg.runtime)

    async def process():
        async for msg in k.execute(exec_msg):
            if msg['msgtype'] == 'write':
                yield msg['data']

    return StreamingResponse(process(), media_type='text/plain')

app = Starlette(routes=[
    Route('/', home),
    Route('/exec', livecode_exec, methods=['POST']),
    WebSocketRoute("/livecode", LiveCode),
    Mount('/static', app=StaticFiles(directory=static_dir), name="static"),
])
