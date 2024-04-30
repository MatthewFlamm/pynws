#!/usr/bin/env bash

git config --global --add safe.directory "$PWD"

python -m pip install -e .
python -m pip install -r requirements-test.txt
python -m pip install pre-commit
pre-commit install --install-hooks
