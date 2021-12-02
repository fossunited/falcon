#! /bin/sh

if [ "$FALCON_MODE" = "test" ]
then
    exec go test
else
    exec go run main.go
fi
