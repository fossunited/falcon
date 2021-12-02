#! /bin/sh
TIMEOUT=10
SOURCE_FILE=${FALCON_SOURCE_FILE:-main.py}

if [ "$FALCON_MODE" = "test" ]
then
    exec timeout $TIMEOUT python /opt/runtests.py "$@"
else
    exec timeout $TIMEOUT python $SOURCE_FILE "$@"
fi
