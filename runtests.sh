#! /bin/bash
#
# Script to run all the tests
#
export PYTHONPATH=.
pytest tests/ $*
