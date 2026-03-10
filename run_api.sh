#!/bin/bash

# Exit immediately if a command fails
set -e

# Activate virtual environment
source venv/bin/activate

# Run FastAPI app with reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
