// Javascript to setup demos on the home page

// Setup demo of using Python
function setupPythonDemo(selector) {
  return new LiveCodeEditor(document.querySelector(selector), {
    base_url: document.location.protocol + "//" + document.location.host,
    runtime: "python",
    codemirror: true
  });
}

const CANVAS_START_PY=`
import sketch

# Execute the code in main.py with all the functions
# defined in sonic.py predefined
code = open("main.py").read()
env = dict(sketch.__dict__)
exec(code, env)
`;

const CANVAS_SKETCH_PY=`
import json
from time import sleep

def sendmsg(msgtype, function, args):
  """Sends a message to the frontend.
  """
  msg = dict(msgtype=msgtype, function=function, args=args)
  print("--MSG--", json.dumps(msg))

def _draw(function, **args):
  sendmsg("draw", function, args)

def circle(x, y, d):
  """Draws a circle of diameter d with center (x, y).
  """
  _draw("circle", x=x, y=y, d=d)

def line(x1, y1, x2, y2):
  """Draws a line from point (x1, y1) to point (x2, y2).
  """
  _draw("line", x1=x1, y1=y1, x2=x2, y2=y2)

def rect(x, y, w, h):
  """Draws a rectangle on the canvas.

  Parameters
  ----------
  x: x coordinate of the top-left corner of the rectangle
  y: y coordinate of the top-left corner of the rectangle
  w: width of the rectangle
  h: height of the rectangle
  """
  _draw("rect", x=x, y=y, w=w, h=h)

def clear():
  _draw("clear")

# clear the canvas on start
clear()
`

CANVAS_FUNCTIONS = {
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
  rect: function(ctx, args) {
    ctx.beginPath();
    ctx.rect(args.x, args.y, args.w, args.h);
    ctx.stroke();
  },
  clear: function(ctx, args) {
    var width = 300;
    var height = 300;
    ctx.clearRect(0, 0, width, height);
  }
}

function drawOnCanvas(canvasElement, funcName, args) {
  var ctx = canvasElement.getContext('2d');
  var func = CANVAS_FUNCTIONS[funcName];

  var scalex = canvasElement.width/300;
  var scaley = canvasElement.height/300;

  ctx.save();
  ctx.scale(scalex, scaley);
  func(ctx, args);
  ctx.restore();
}

// Setup the demo for using Python with HTML5 canvas
function setupCanvasDemo(selector) {
  return new LiveCodeEditor(document.querySelector(selector), {
    base_url: document.location.protocol + "//" + document.location.host,
    runtime: "python",
    codemirror: true,
    files: [
      {filename: "start.py", contents: CANVAS_START_PY},
      {filename: "sketch.py", contents: CANVAS_SKETCH_PY},
    ],
    env: {
      "FALCON_SOURCE_FILE": "start.py",
    },
    onMessage: {
      draw: function(editor, msg) {
        const canvasElement = editor.parent.querySelector(".canvas");
        drawOnCanvas(canvasElement, msg.function, msg.args);
      }
    }
  });
}

const MUSIC_START_PY=`
import sonic

# Execute the code in main.py with all the functions
# defined in sonic.py predefined
code = open("main.py").read()
env = dict(sonic.__dict__)
exec(code, env)
`;

const MUSIC_SONIC_PY=`
import json
from time import sleep

def sendmsg(msgtype, **cmd):
  """Sends a message to the frontend.
  """
  msg = dict(msgtype=msgtype, cmd=cmd)
  print("--MSG--", json.dumps(msg))

def play(note):
  sendmsg("play", function="play", note=note)
`;

// Setup the demo for playing music with Python using Tone.js library
function setupMusicDemo(selector) {
  const synth = new Tone.Synth().toDestination();

  return new LiveCodeEditor(document.querySelector(selector), {
    base_url: document.location.protocol + "//" + document.location.host,
    runtime: "python",
    files: [
      {filename: "start.py", contents: MUSIC_START_PY},
      {filename: "sonic.py", contents: MUSIC_SONIC_PY},
    ],
    env: {
      "FALCON_SOURCE_FILE": "start.py",
    },
    codemirror: true,
    onMessage: {
      play: function(editor, msg) {
        synth.triggerAttackRelease(msg.cmd.note, "8n")
      }
    }
  });
}
