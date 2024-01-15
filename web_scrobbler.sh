#!/bin/bash

SCRIPT_DIR=$(dirname "$0")
SCROBBLER_PATH="$SCRIPT_DIR/web_scrobbler.py"

# Check if port 5000 is in use
if lsof -i:5000 >/dev/null; then
    echo "Port 5000 is in use, opening the browser..."
else
    echo "Port 5000 is not in use, starting the Flask app..."
    # Start your Flask app in the background
    # Replace 'python3 path/to/your/app.py' with the correct command to start your Flask app
    python3 $SCROBBLER_PATH &
    sleep 2 # Wait a bit for the server to start
    # Open the browser
fi
$BROWSER --new-window http://localhost:5000
