

setup:
	docker pull python:3.9
	cd runtimes/python-canvas && docker build -t livecode-python-canvas .
