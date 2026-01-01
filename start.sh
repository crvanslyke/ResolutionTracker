#!/bin/bash

# Virtue Habit Tracker - Quick Start Script

echo "Starting Virtue Habit Tracker..."
echo "================================"
echo ""

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Initialize database if it doesn't exist
if [ ! -f habits.db ]; then
    echo "Initializing database..."
    python database.py
    echo ""
fi

echo "Starting Flask application..."
echo "Access the app at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"
echo ""

python app.py
