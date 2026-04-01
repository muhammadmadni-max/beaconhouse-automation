#!/bin/bash

# Exit immediately if a command fails
set -e
cd /home/datanext/automation/
# Activate virtual environment
source venv/bin/activate
export PYTHONUNBUFFERED=1
# export DISPLAY=:99

# # Xvfb :99 -screen 0 1920x1080x24 &
# # Start Xvfb only if not already running
# if ! pgrep -x "Xvfb" > /dev/null
# then
#     Xvfb :99 -screen 0 1920x1080x24 &
#     sleep 2
# fi

# Run FastAPI app with reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
