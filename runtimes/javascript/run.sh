#!/bin/sh

if [ "$FALCON_MODE" = "test" ]; then
    echo "Test mode is not supported for JavaScript yet"
    exit 1
else
    exec node /app/main.js
fi