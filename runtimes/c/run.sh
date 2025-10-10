#!/bin/sh
set -e

SOURCE_FILE="main.c"
TEMP_SOURCE="/tmp/main.c"
OUTPUT_BINARY="/tmp/a.out"

cp "${SOURCE_FILE}" "${TEMP_SOURCE}"
gcc "${TEMP_SOURCE}" -o "${OUTPUT_BINARY}"
exec "${OUTPUT_BINARY}"