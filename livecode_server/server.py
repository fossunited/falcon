"""livecode server.
"""
from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.responses import JSONResponse
from starlette.routing import Route, WebSocketRoute
from starlette.templating import Jinja2Templates

from .kernel import Kernel
from .utils import templates_dir

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
            await self.on_exec(ws, msg)
        else:
            await self.on_unknown_message(ws, msg)

    async def on_ping(self, ws, msg):
        await ws.send_json({"msgtype": "pong"})

    async def on_quit(self, ws, msg):
        await ws.send_json({"msgtype": "goodbye"})
        await ws.close()

    async def on_exec(self, ws, msg):
        runtime = msg['runtime']
        code = msg['code']
        env = msg.get('env') or {}

        k = Kernel(ws, runtime)
        await k.execute(code, env)
        await ws.close()

    async def on_unknown_message(self, ws, msg):
        msgtype = msg.get("msgtype")
        await ws.send_json({
            "msgtype": "error",
            "error": f"Unknown message type: {msgtype}",
            "msg": msg
        })

app = Starlette(routes=[
    Route('/', home),
    WebSocketRoute("/livecode", LiveCode)
])