#!/bin/bash

# Quick start - just run this!
echo "Starting WiFi Motion Detector Dashboard..."
echo ""

cd "$(dirname "$0")"

# Get IP
IP=$(hostname -I | awk '{print $1}')

echo "========================================"
echo "🌐 Dashboard is starting..."
echo "========================================"
echo ""
echo "📱 Open this link on your phone:"
echo ""
echo "   http://$IP:5000"
echo ""
echo "========================================"
echo ""

python3 web_dashboard.py
