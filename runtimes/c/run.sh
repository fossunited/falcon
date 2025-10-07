#!/bin/sh
set -e
SOURCE_FILE="main.c"
OUTPUT_BINARY="/tmp/a.out"

compile_and_run() {
    gcc "${SOURCE_FILE}" -o "${OUTPUT_BINARY}"
    exec "${OUTPUT_BINARY}"
}

if [ "$FALCON_MODE" = "test" ]
then
    compile_and_run
else
    compile_and_run
fi
