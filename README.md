# [<>] Falcon - Run code directly from your browser

Falcon is a service that execute code in any programming language in a sandboxed environment.

It uses websockets for bidrectional communication and can support interactive applications with support for keyboard and mouse.

## Requirements

Falcon runs on any unix computer and the following software are required.

* Python 3
* Docker

## The Setup

Step 1: Clone the repository

```
$ git clone https://github.com/fossunited/falcon

$ cd livecode
```

Step 2: Install Python dependencies. You may want to do this in a virtualenv.

```
$ pip install -r requirements.txt -r dev-requirements.txt
```

Step 3: Build the required docker images

```
$ make setup
```

Step 4: Start the falcon server

```
$ uvicorn livecode_server.server:app
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
...
```

Step 5: visit the webapp at <http://127.0.0.1:8000/>.

## Running Tests

Tests are written using pytest.

To run tests:

```
$ ./runtests.sh
...
collected 2 items

tests/test_livecode.py ..
```

Or:

```
$ ./runtests.sh
...
collected 2 items

tests/test_livecode.py::test_fileformats[sessions/test_hello.yml] PASSED
tests/test_livecode.py::test_fileformats[sessions/test_ping.yml] PASSED
```

As you notice, the tests are written in YAML files. See [tests/](tests/) to understand how to write tests.

## The Client Library

The falcon also comes with a `livecode.js` library. It is available at path `/static/livecode.js` on the livecode server.

### `LiveCodeSession`

Creates a session with the live code server.

```
var session = LiveCodeSession({
    base_url: "https://livecode.example.com",
    runtime: python,
    code: "print('hello, world!')",
    onMessage: function(msg) {
        console.log(msg);
    }
})
```

The `LiveCodeSession` takes options as an object. The following fields are supported:

**`base_url`**: _Required_

The base URL of the livecode server.

**`runtime`**:

The runtime to use. Currently only `python` runtime is supported and that is the default value.

**`code`**: _Required_

The code to execute.

By default, this code is saved as `main.py` and that is executed.

**`code_filename`**:

Filename to use to save the code. The default value depends on the runtime. For `python` runtime, the default value is `main.py`.

**`files`**:

List of files to to save in the working directory before executing the code. Each file is specified as an object with `filename` and `contents` fields.

```
[
    {filename: "sq.py", contents: "def square(x): return x*x"}
]
```

**`command`**:

Command to execute, specified as a list.

```
["python", "start.py"]
```

Typically used along with `files` to use a different startup script.

**`env`**:

Environment variables to set. Specified as an object.

**`onMessage`**:

Function to call when a message is received. The function gets the message as argument.

### `LiveCodeEditor`

The `LiveCodeEditor` provides a high-level editor interface taking care of session creation when run button is clicked and displaying output.

```
<div class="code-editor" id="editor-1">
    <div>
        <textarea class="code">print("hello, world!")</textarea>
    </div>
    <div>
        <button class="run">Run</button>
    </div>
    <pre class="output">
    </pre>
</div>

<script type="text/javascript>
var e = document.getElementById("editor-1")
var editor = LiveCodeEditor(e, {
    base_url: "https://livecode.example.com",
    runtime: python,
    code: "print('hello, world!')",
    codemirror: true
})
</script>
```

It looks for elements with the following class names under the specified element.

**`code`**

The textarea with the code. This code is executed when the run button/link is clicked.

**`run`**

The link or button to attach the run action.

**`output`**

The element to write the output.


The `LiveCodeEditor` supports all options that `LiveCodeSession` supports and the following:

**`codemirror`**

Enables codemirror when this is set to `true`. The codemirror js and css assets must be included in the document for this to work.

## Low-level Interaction

Install `wscat`:

```
$ npm install -g wscat
```

Start interacting with the live code server:

```
$ wscat --connect http://127.0.0.1:8000/livecode
Connected (press CTRL+C to quit)
< {"msgtype": "welcome", "message": "welcome to livecode"}
> {"msgtype": "ping"}
< {"msgtype": "pong"}
> {"msgtype": "exec", "runtime": "python", "code": "print('hello, world!')"}
> {"msgtype": "write", "file": "stdout", "data": "hello, world!\n"}
> {"msgtype": "quit"}
< {"msgtype": "goodbye"}
```

## The Live Code Protocol

The client and server communicate over websockets using simple JSON messages.

The following types of messages are accepted by the server.

**`ping`**

A ping message. The server responds back with a `pong` message.

Example:

```
{"msgtype": "ping"}
```

**`exec`**

Request to execute a piece of code. The message will have `runtime`, `files` and `entrypoint` fields.

supported fields:
```
runtime [required] - execution runtime to use
code [required] - the code to execute
env [optional] - environment variables specified as an object
timeout [optional] - timeout in milliseconds
```

Example:

```
{
  "msgtype": "exec",
  "runtime": "python",
  "code": "print('hello, world!')",
  "timeout": 5000
}
```

**`quit`**

Request to quit the connection.

Example:

```
{"msgtype": "quit"}
```

**`event`**

Notification sent by the client when specific events happen on the server.
The server will not consume this message directly, but makes it available
for the application to receive it.

supported fields:
```
event [required] - name of the event. for example: mousemove
data [required] - data about the event. This will be specific to each type of event.
```

The following types of messages are sent by the server.

**`pong`**

Sent as a response to the ping message.

Example:

```
{"msgtype": "pong"}
```

**`goodbye`**

Sent as a response to the `quit` message.

Example:

```
{"msgtype": "goodbye"}
```

**`write`**

Sent when something is printed to `stdout` or `stderr`.

Example:

```
{"msgtype": "write", "file": "stdout", "data": "hello, world!\n"}
```

As of now, there is no support for printing binary data.

**`exitstatus`**

Sent after the execution is complete.

Example:

```
{"msgtype": "exitstatus", "exitstatus": 0}
```

**`error`**

Sent when a received message can not be processed by the server.

Example:

```
{"msgtype": "error", "error": "unknown message type: qiut", "msg": {"msgtype
": "qiut"}}
```

Apart from these messages, the application can send custom messages.
For example, a program can send a message to draw on a canvas.

```
{"msgtype": "draw", "shape": "circle", "args": [100, 100, 50]}
```

## New API

Execute code:

```
POST /runtimes/python

print("hello, world!")
---
HTTP/1.1 200 OK

hello, world!
```

Run tests:

```
$ curl -Fmain.py=@main.py -F test_main.py=test_main.py -H 'X-FALCON-MODE: test' http://localhost:8010/runtimes/python
```

**Headers**

* `X-FALCON-MODE` - `exec` or `test`
* `X-FALCON-ARGS` - command-line arguments passed
* `X-FALCON-ENV` - space separated env variables 'FOO=bar X=1'

## LICENSE

This repository has been released under the [MIT License](https://github.com/fossunited/falcon/blob/main/LICENSE).

