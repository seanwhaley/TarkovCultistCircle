#!/bin/bash

# Get absolute path to project root
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found! Please run setup.sh first."
    exit 1
fi

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    source .venv/bin/activate
fi

# Set up Python path to include src directory
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

# Run the application
python wsgi.py
