#! /bin/sh
TIMEOUT=10

if [ "$FALCON_MODE" = "test" ]
then
    exec timeout $TIMEOUT python /opt/runtests.py "$@"
else
    exec timeout $TIMEOUT python main.py "$@"
fi
