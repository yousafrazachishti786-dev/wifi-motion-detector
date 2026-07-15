#!/bin/bash

# WiFi Motion Detector - Simple Setup Script
# Run this once and everything will be configured

echo ""
echo "========================================"
echo "WiFi Motion Detector Setup"
echo "========================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️  Not detected as Raspberry Pi"
    echo "This script works best on Raspberry Pi"
    echo ""
fi

# Step 1: Install dependencies
echo "[1/4] Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y python3 python3-pip python3-dev wireless-tools iw > /dev/null 2>&1
echo "✓ System packages installed"
echo ""

# Step 2: Install Python packages
echo "[2/4] Installing Python packages..."
sudo pip3 install -q -r requirements-web.txt
echo "✓ Python packages installed"
echo ""

# Step 3: Create startup script
echo "[3/4] Creating startup script..."
cat > start_dashboard.sh << 'EOF'
#!/bin/bash
cd $(dirname "$0")
python3 web_dashboard.py
EOF
chmod +x start_dashboard.sh
echo "✓ Startup script created"
echo ""

# Step 4: Get IP address
echo "[4/4] Getting your Raspberry Pi IP address..."
IP=$(hostname -I | awk '{print $1}')
echo ""
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "🚀 To START the dashboard, run:"
echo ""
echo "   ./start_dashboard.sh"
echo ""
echo "📱 Then open on your phone browser:"
echo ""
echo "   http://$IP:5000"
echo ""
echo "⛔ To STOP the dashboard, press Ctrl+C"
echo ""
echo "========================================"
echo ""
