LIVECODE_PORT?=8000

default: run

setup:
	docker pull python:3.9
	docker pull rust:1.55-alpine
	docker pull golang:1.17
	@[ -d .git ] && echo "flake8" > .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit; true

run:
	uvicorn livecode_server.server:app --port ${LIVECODE_PORT}
