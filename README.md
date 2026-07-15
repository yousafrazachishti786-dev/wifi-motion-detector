# WiFi Motion Detector

A Python-based motion detection system using WiFi signal strength (RSSI) analysis.

## Features
- Real-time RSSI monitoring
- Motion detection via signal variance analysis
- Configurable sensitivity thresholds
- Support for Raspberry Pi and Linux systems
- Optional alerting system
- MQTT integration for smart home automation

## Requirements
- Python 3.7+
- Linux/Raspberry Pi OS
- WiFi adapter supporting iwconfig

## Quick Installation

```bash
git clone https://github.com/yousafrazachishti786-dev/wifi-motion-detector.git
cd wifi-motion-detector
bash install.sh
```

## Quick Start

### Basic Usage
```bash
python3 detector.py --interface wlan0 --threshold 3
```

### With GPIO Buzzer Alert (Raspberry Pi)
```bash
python3 detector.py --alert --port 17
```

### With MQTT Publishing
```bash
python3 mqtt_publisher.py --broker 192.168.1.100 --topic home/motion
```

## Command Line Options

```
Usage: detector.py [OPTIONS]

Options:
  -i, --interface TEXT      WiFi interface (default: wlan0)
  -t, --threshold FLOAT     Variance threshold (default: 3)
  -w, --window INT          Window size for analysis (default: 10)
  --interval FLOAT          Reading interval in seconds (default: 1)
  -d, --duration FLOAT      Run duration in seconds (default: infinite)
  -a, --alert              Enable GPIO buzzer alert (requires RPi)
  -p, --port INT           GPIO port for buzzer (default: 17)
```

## How It Works

1. **RSSI Monitoring**: Continuously reads WiFi signal strength from the specified interface
2. **Variance Analysis**: Calculates signal variance over a moving window
3. **Motion Detection**: When variance exceeds threshold, motion is detected
4. **Alerting**: Optional GPIO buzzer or MQTT alerts on motion events

## Configuration Files

- `.env` - Configuration variables (copy from `.env.example`)
- `docker-compose.yml` - MQTT broker setup for testing

## Hardware Setup

### Raspberry Pi GPIO (Optional Buzzer)
```
GPIO 17 (pin 11) -> Buzzer positive
GND (pin 6)      -> Buzzer negative
```

### Finding Your WiFi Interface
```bash
iwconfig
# or
ip link show
```

## Testing

### Test Motion Detection
```bash
# Terminal 1: Run detector
python3 detector.py --threshold 2

# Terminal 2: Move around the WiFi signal area
# Watch for motion detection in Terminal 1
```

### Test MQTT
```bash
# Start MQTT broker
docker-compose up -d

# Run detector with MQTT
python3 mqtt_publisher.py --broker localhost

# In another terminal, subscribe to events
mosquitto_sub -h localhost -t 'home/motion/#'
```

## Troubleshooting

### No RSSI readings
```bash
# Check WiFi interface
iwconfig

# Try different interface
python3 detector.py --interface wlan1
```

### Permission denied (GPIO)
```bash
# Run with sudo for GPIO access
sudo python3 detector.py --alert
```

### MQTT connection failed
```bash
# Verify broker is running
pingpong broker_address

# Check credentials in .env
```

## Advanced Usage

### Systemd Service (Auto-start on boot)

```bash
# Create service file
sudo nano /etc/systemd/system/wifi-motion.service
```

Add:
```ini
[Unit]
Description=WiFi Motion Detector
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/wifi-motion-detector
ExecStart=/usr/bin/python3 detector.py --interface wlan0 --threshold 3
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable wifi-motion.service
sudo systemctl start wifi-motion.service
```

### Cron Job
```bash
# Run every 5 minutes
*/5 * * * * cd /home/pi/wifi-motion-detector && python3 detector.py --duration 300
```

## Performance Tips

1. **Adjust threshold**: Lower threshold = more sensitive, higher = less sensitive
2. **Adjust window size**: Larger window = smoother but slower detection
3. **Adjust interval**: Smaller interval = faster detection, more CPU usage
4. **WiFi placement**: Keep router away from other RF sources

## Project Structure

```
wifi-motion-detector/
├── detector.py              # Main motion detector
├── mqtt_publisher.py        # MQTT integration
├── requirements.txt         # Python dependencies
├── setup.py                # Package setup
├── install.sh              # Installation script
├── docker-compose.yml      # MQTT broker for testing
├── .env.example            # Configuration template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Supported Platforms

- ✅ Raspberry Pi 3, 4, 5
- ✅ Linux laptops/desktops
- ✅ Any system with Python 3.7+ and WiFi interface
- ⚠️ macOS (iwconfig not available, needs modification)
- ❌ Windows (iwconfig not available)

## License

MIT License

## Contributing

Contributions welcome! Feel free to open issues or submit PRs.

## Disclaimer

This project is for educational and personal use. Ensure you have permission to monitor WiFi signals in your environment.
