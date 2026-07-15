#!/bin/bash

# WiFi Motion Detector Installation Script

echo "===================================="
echo "WiFi Motion Detector Setup"
echo "===================================="

# Check if running on Raspberry Pi
if [ -f /proc/device-tree/model ]; then
    echo "Detected Raspberry Pi"
    IS_RPI=true
else
    echo "Not running on Raspberry Pi (some features may be unavailable)"
    IS_RPI=false
fi

# Update system
echo "\nUpdating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
echo "\nInstalling dependencies..."
sudo apt-get install -y python3 python3-pip python3-dev
sudo apt-get install -y wireless-tools iw

# Install Python packages
echo "\nInstalling Python packages..."
pip3 install -r requirements.txt

# Install RPi.GPIO for Raspberry Pi
if [ "$IS_RPI" = true ]; then
    echo "\nInstalling Raspberry Pi GPIO library..."
    sudo pip3 install RPi.GPIO
fi

# Create .env file
if [ ! -f .env ]; then
    echo "\nCreating .env configuration file..."
    cp .env.example .env
    echo ".env created. Please edit with your settings."
fi

# Make scripts executable
chmod +x detector.py
chmod +x mqtt_publisher.py
chmod +x install.sh

echo "\n===================================="
echo "Installation Complete!"
echo "===================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your WiFi interface and settings"
echo "2. Run: python3 detector.py"
echo "3. Or with MQTT: python3 mqtt_publisher.py --broker <your-broker>"
echo ""
echo "For more info, see README.md"
