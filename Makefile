
default: run

setup:
	docker pull python:3.9
	cd runtimes/python-canvas && docker build -t livecode-python-canvas .

run:
	uvicorn livecode_server.server:app
