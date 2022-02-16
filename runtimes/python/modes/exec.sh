#! /bin/bash
#
# Script invoked to on "exec" mode
#
SOURCE_FILE=${FALCON_SOURCE_FILE:-"main.py"}

exec python $SOURCE_FILE "$@"
