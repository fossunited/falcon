#!/bin/sh
set -e

SOURCE_FILE="main.c"
OUTPUT_BINARY="/tmp/a.out"

gcc "${SOURCE_FILE}" -o "${OUTPUT_BINARY}"
exec "${OUTPUT_BINARY}"
