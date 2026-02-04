#!/bin/bash
# Railway startup script

# Start health check server in background
python health_server.py &

# Wait a moment for health server to start
sleep 2

# Start the main heartbeat orchestrator
python heartbeat.py