#!/bin/bash
# Start script for NDIS Decoder backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set default port if not specified
export PORT=${PORT:-8000}

# Start the application using gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
