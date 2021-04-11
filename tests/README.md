# Tests

LiveCode tests are written as yaml files.

Each yaml file corresponds to one test with multiple steps. Each step is either a `send` or a `recv` operation. There is test runner, that reads the yaml files and executes each step, verifying the data received from the app is matching what is specified in the test file.

For example, let's look at the ping test (see [sessions/test_ping.yml](sessions/test_ping.yml)).

```
- recv:
    msgtype: welcome
    message: welcome to livecode
- send:
    msgtype: ping
- recv:
    msgtype: pong
```

This has three steps.
1. When the connection is estabilished the server greets with a welcome message. All the tests will have this as the first step.
2. We are sending a _ping_ message to the server.
3. After sending the _ping_ message, the server should respond back with _pong_ message. We are verifying that adding a `recv` step with the expected message.

Similarly, to test helloworld, we would write something like this:

```
- recv:
    msgtype: welcome
    message: welcome to livecode
- send:
    msgtype: exec
    runtime: python
    code: print("hello, world!")
- recv:
    msgtype: write
    file: stdout
    data: "hello, world!\n"
```

Do you want to try adding a new test?
