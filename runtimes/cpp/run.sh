#!/bin/sh
set -e

SOURCE_FILE="main.cpp"
OUTPUT_BINARY="/tmp/a.out"

g++ "${SOURCE_FILE}" -o "${OUTPUT_BINARY}"
exec "${OUTPUT_BINARY}"

