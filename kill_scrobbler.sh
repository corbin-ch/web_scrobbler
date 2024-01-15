#!/bin/bash

# Find the PID of the process using port 5000
pid=$(lsof -t -i:5000)

# Check if the PID exists
if [ -n "$pid" ]; then
    echo "Stopping the Flask server running on port 5000..."
    # Kill the process
    kill $pid

    if [ $? -eq 0 ]; then
        echo "Server stopped successfully."
    else
        echo "Failed to stop the server. You might need to run the script with sudo."
    fi
else
    echo "No server is running on port 5000."
fi
