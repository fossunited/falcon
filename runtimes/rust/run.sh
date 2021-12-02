#! /bin/sh

if [ "$FALCON_MODE" = "test" ]
then
    echo "tests are not yet supported for rust"
    exit 1
else
    rustc main.rs && ./main
fi
