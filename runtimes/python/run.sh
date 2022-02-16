#! /bin/sh
TIMEOUT=10
SOURCE_FILE=${FALCON_SOURCE_FILE:-"main.py"}
MODE=${FALCON_MODE:-"exec"}
SCRIPT=/opt/modes/$MODE.sh

if [ -x "$SCRIPT" ]
then
    exec timeout $TIMEOUT $SCRIPT "$@"
else
    echo "ERROR: invalid mode - $MODE" 1>&2
    exit 1
fi
