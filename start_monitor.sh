#!/bin/bash

# Set working directory
cd /home/sovol/printer_monitor

# Check if the monitor script is already running
if pgrep -f printer_monitor.py > /dev/null; then
    echo "Printer monitor is already running. Skipping launch."
    exit 0
fi

# Launch the monitor script in the background and log output
nohup python3 printer_monitor.py > debug_output.log 2>&1 &

# Print confirmation to Klipper terminal
echo "Printer monitor launched successfully."

