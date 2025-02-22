#!/bin/bash
export PYTHONPATH="$(pwd)/src:${PYTHONPATH}"
python wsgi.py
