
// Connection to a LiveCode session
//
// USAGE:
//
//  var livecode = new LiveCodeSession({
//    base_url: "http://livecode.example.com/",
//    runtime: "python",
//    code: "print('hello, world!')",
//    onMessage: (msg) => console.log(msg)
//  })
class LiveCodeSession {
  constructor(options) {
    this.options = options;
    this.base_url = new URL(options.base_url);
    this.runtime = options.runtime;
    this.code = options.code;
    this.onMessage = options.onMessage || null;

    this.ws = this.createWebSocket();
    this.send({"msgtype": "exec", "runtime": this.runtime, "code": this.code})
  }

  createWebSocket() {
    let protocol = this.base_url.protocol == "https:" ? "wss:" : "ws:";
    let ws_url = protocol + "//" + this.base_url.host + "/livecode";
    let ws = new WebSocket(ws_url);
    ws.addEventListener("open", (ev) => this.processOpen(ev));
    ws.addEventListener("close", (ev) => this.processClose(ev));
    ws.addEventListener("message", (ev) => this.processMessage(ev));
    ws.addEventListener("error", (ev) => this.processError(ev));
    return ws;
  }

  close() {
    if (this.ws) {
      this.ws.close(1000)
      this.ws =  null;
    }
  }

  processOpen(ev) {
  }
  processClose(ev) {
  }
  processMessage(ev) {
    let msg = JSON.parse(ev.data);
    if (this.onMessage) {
      this.onMessage(msg)
    }
  }
  processError(ev) {
  }

  waitForOpen(ws, func) {
    if (ws.readyState == ws.OPEN) {
      func()
    }
    else {
      setTimeout(() => this.waitForOpen(ws, func), 1)
    }
  }

  send(msg) {
    var ws = this.ws;
    this.waitForOpen(ws, () => {
      ws.send(JSON.stringify(msg))
    })
  }
}

// Initialized the editor and all controls.
// It is expected that the given element is a parent element
// with textarea, div.output, button.run optionally canvas.canvas
// elements in it.
class LiveCodeEditor {
  constructor(element, options) {
    this.options = options;
    this.parent = element;

    this.base_url = options.base_url;
    this.runtime = options.runtime;

    this.session = null;

    this.elementCode = this.parent.querySelector(".code");
    this.elementOutput = this.parent.querySelector(".output");
    this.elementRun = this.parent.querySelector(".run");
    this.elementCanvas = this.parent.querySelector(".canvas");

    this.setupActions()
  }
  reset() {
    if (this.session) {
      this.session.close();
      this.session = null;
    }
    this.clearOutput();
    this.clearCanvas();
  }
  setupActions() {
    this.elementRun.onclick = () => {
      var code =
      this.reset();
      this.session = new LiveCodeSession({
        base_url: this.base_url,
        runtime: this.runtime,
        code: this.elementCode.value,
        onMessage: (msg) => this.onMessage(msg)
      });
    };
  }

  onMessage(msg) {
    if (msg.msgtype == 'write') {
      this.writeOutput(msg.data);
    }
    else if (msg.msgtype == 'draw') {
      this.drawOnCanvas(msg.cmd)
    }
  }

  drawOnCanvas(cmd) {
    var functions = {
      circle: function(ctx, args) {
        ctx.beginPath();
        ctx.arc(args.x, args.y, args.d/2, 0, 2*Math.PI);
        ctx.stroke();
      },
      line: function(ctx, args) {
        ctx.beginPath();
        ctx.moveTo(args.x1, args.y1);
        ctx.lineTo(args.x2, args.y2);
        ctx.stroke();
      },
      clear: function(ctx, args) {
        clearCanvas();
      }
    }
    if (!this.elementCanvas) {
      return
    }

    var ctx = this.elementCanvas.getContext('2d');
    var name = cmd['function']
    var func = functions[name]
    func(ctx, cmd)
  }

  clearCanvas() {
    if (!this.elementCanvas) {
      return
    }
    var ctx = this.elementCanvas.getContext('2d');
    var width = this.elementCanvas.width;
    var height = this.elementCanvas.height;
    ctx.clearRect(0, 0, width, height);
  }

  clearOutput() {
    if (this.elementOutput) {
      this.elementOutput.innerHTML = "";
    }
  }

  writeOutput(data) {
    if (this.elementOutput) {
      this.elementOutput.innerHTML += data;
    }
  }
}
