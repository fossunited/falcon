#! /bin/bash
SOURCE_FILE=${FALCON_SOURCE_FILE:-"main.py"}

exec mypy $SOURCE_FILE
