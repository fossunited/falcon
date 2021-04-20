"""Startup script for python-canvas runtime of livecode.

It adds the functionis circle and line to the builtins before
calling main.py.
"""
import os.path
import json

def _draw(function, **kwargs):
    # HACK: currently we are using prefix --MSG-- to indicate
    # that this is a custom message
    msg = dict(msgtype="draw", cmd=dict(function=function, **kwargs))
    print("--MSG--", json.dumps(msg))

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

__builtins__.circle = circle
__builtins__.line = line
__builtins__.rect = rect

if os.path.exists("main.py"):
    exec(open("main.py").read())
