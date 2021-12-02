LIVECODE_PORT?=8000

default: run

setup:
	docker pull fossunited/falcon-python:3.9
	docker pull fossunited/falcon-golang
	docker pull fossunited/falcon-rust
	@[ -d .git ] && echo "flake8" > .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit; true

run:
	uvicorn livecode_server.server:app --port ${LIVECODE_PORT}
