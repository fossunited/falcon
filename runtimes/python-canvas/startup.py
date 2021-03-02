"""Startup script for python-canvas runtime of livecode.

It adds the functionis circle and line to the builtins before
calling main.py.
"""
import os.path
import json

def _draw(function, **kwargs):
    # HACK: currently we are using prefix --DRAW-- to indicate
    # that this is command to draw to the canvas, not a print statement.
    print("--DRAW--", json.dumps(dict(function=function, **kwargs)))

def circle(x, y, d):
    _draw("circle", x=x, y=y, d=d)

def line(x1, y1, x2, y2):
    _draw("line", x1=x1, y1=y1, x2=x2, y2=y2)

def clear():
    _draw("clear")

__builtins__.circle = circle
__builtins__.line = line

if os.path.exists("main.py"):
    exec(open("main.py").read())
