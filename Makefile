LIVECODE_PORT?=8010

default: run

build-c-runtime:
	docker build -t fossunited/falcon-c ./runtimes/c

setup: build-c-runtime
	docker pull fossunited/falcon-python:3.9
	docker pull fossunited/falcon-golang
	docker pull fossunited/falcon-rust
	@[ -d .git ] && echo "flake8" > .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit; true

run:
	uvicorn livecode_server.server:app --host 0.0.0.0 --port ${LIVECODE_PORT}
