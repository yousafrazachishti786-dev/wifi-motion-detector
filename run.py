#!/usr/bin/env python3
"""
ONE FILE - Just run this!
Everything happens automatically.
"""

import os
import sys
import subprocess
import socket

def get_ip():
    """Get Raspberry Pi IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def main():
    print("\n" + "="*60)
    print("WiFi Motion Detector - Automatic Setup")
    print("="*60 + "\n")
    
    # Step 1: Check Python packages
    print("[1/3] Checking packages...")
    try:
        import flask
        import flask_cors
        print("✓ All packages ready\n")
    except ImportError:
        print("⚠ Installing packages (this takes 1-2 minutes)...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements-web.txt"])
        print("✓ Packages installed\n")
    
    # Step 2: Show IP
    print("[2/3] Getting IP address...")
    ip = get_ip()
    print(f"✓ Your IP: {ip}\n")
    
    # Step 3: Start server
    print("[3/3] Starting dashboard...\n")
    print("="*60)
    print("✅ READY! Open on your phone:")
    print("="*60)
    print(f"\n   http://{ip}:5000\n")
    print("="*60)
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Import and run dashboard
    from web_dashboard import app
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Dashboard stopped")
        sys.exit(0)
