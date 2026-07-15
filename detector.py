#!/usr/bin/env python3
"""
WiFi Motion Detector
Detects motion using RSSI signal strength variations
"""

import subprocess
import time
import statistics
import argparse
import json
from datetime import datetime
from collections import deque
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('motion_detector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WiFiMotionDetector:
    """Motion detection using WiFi RSSI analysis"""
    
    def __init__(self, interface='wlan0', threshold=3, window_size=10, alert=False, port=17):
        """
        Initialize WiFi Motion Detector
        
        Args:
            interface: WiFi interface name (default: wlan0)
            threshold: Variance threshold for motion detection
            window_size: Number of readings to analyze
            alert: Enable GPIO alert (requires RPi.GPIO)
            port: GPIO pin for alert buzzer
        """
        self.interface = interface
        self.threshold = threshold
        self.window_size = window_size
        self.rssi_history = deque(maxlen=window_size)
        self.motion_detected = False
        self.alert_enabled = alert
        self.gpio_port = port
        self.start_time = datetime.now()
        self.motion_count = 0
        
        if self.alert_enabled:
            self._setup_gpio()
        
        logger.info(f"WiFi Motion Detector initialized on {interface}")
        logger.info(f"Threshold: {threshold}, Window Size: {window_size}")
    
    def _setup_gpio(self):
        """Setup GPIO for buzzer alert"""
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gpio_port, GPIO.OUT)
            GPIO.output(self.gpio_port, GPIO.LOW)
            logger.info(f"GPIO setup complete on pin {self.gpio_port}")
        except ImportError:
            logger.warning("RPi.GPIO not available, skipping GPIO setup")
            self.alert_enabled = False
        except RuntimeError:
            logger.warning("GPIO setup failed, running without alerts")
            self.alert_enabled = False
    
    def get_rssi(self):
        """
        Get RSSI value from WiFi interface
        
        Returns:
            int: RSSI value in dBm, or None if unavailable
        """
        try:
            output = subprocess.check_output(
                ['iwconfig', self.interface],
                stderr=subprocess.STDOUT,
                text=True
            )
            
            for line in output.split('\n'):
                if 'Signal level' in line:
                    # Parse RSSI value
                    parts = line.split('Signal level=')
                    if len(parts) > 1:
                        rssi_str = parts[1].split()[0]
                        try:
                            rssi = int(rssi_str)
                            return rssi
                        except ValueError:
                            return None
            return None
        except Exception as e:
            logger.error(f"Error getting RSSI: {e}")
            return None
    
    def detect_motion(self):
        """
        Detect motion based on RSSI variance
        
        Returns:
            bool: True if motion detected, False otherwise
        """
        rssi = self.get_rssi()
        
        if rssi is None:
            logger.warning("Could not read RSSI")
            return False
        
        self.rssi_history.append(rssi)
        
        # Need minimum readings for variance calculation
        if len(self.rssi_history) < self.window_size:
            return False
        
        try:
            # Calculate variance
            variance = statistics.variance(list(self.rssi_history))
            
            # Motion detected if variance exceeds threshold
            motion = variance > self.threshold
            
            if motion and not self.motion_detected:
                self.motion_detected = True
                self.motion_count += 1
                logger.info(f"MOTION DETECTED! Variance: {variance:.2f}")
                
                if self.alert_enabled:
                    self._trigger_alert()
            elif not motion and self.motion_detected:
                self.motion_detected = False
                logger.info("Motion stopped")
                
                if self.alert_enabled:
                    self._stop_alert()
            
            return motion
        except Exception as e:
            logger.error(f"Error in motion detection: {e}")
            return False
    
    def _trigger_alert(self):
        """Trigger GPIO buzzer alert"""
        if self.alert_enabled:
            try:
                import RPi.GPIO as GPIO
                GPIO.output(self.gpio_port, GPIO.HIGH)
            except Exception as e:
                logger.error(f"Error triggering alert: {e}")
    
    def _stop_alert(self):
        """Stop GPIO buzzer alert"""
        if self.alert_enabled:
            try:
                import RPi.GPIO as GPIO
                GPIO.output(self.gpio_port, GPIO.LOW)
            except Exception as e:
                logger.error(f"Error stopping alert: {e}")
    
    def get_stats(self):
        """
        Get detector statistics
        
        Returns:
            dict: Statistics about detection
        """
        uptime = datetime.now() - self.start_time
        current_rssi = self.get_rssi()
        
        stats = {
            'uptime_seconds': uptime.total_seconds(),
            'motion_events': self.motion_count,
            'current_rssi': current_rssi,
            'current_status': 'MOTION' if self.motion_detected else 'IDLE',
            'readings_in_window': len(self.rssi_history),
            'threshold': self.threshold
        }
        
        if len(self.rssi_history) > 1:
            stats['signal_variance'] = statistics.variance(list(self.rssi_history))
            stats['signal_mean'] = statistics.mean(list(self.rssi_history))
        
        return stats
    
    def run(self, interval=1, duration=None):
        """
        Run continuous motion detection
        
        Args:
            interval: Reading interval in seconds
            duration: Run duration in seconds (None for infinite)
        """
        logger.info("Starting motion detection loop")
        print("\n" + "="*60)
        print("WiFi Motion Detector Started")
        print("="*60)
        print(f"Interface: {self.interface}")
        print(f"Threshold: {self.threshold}")
        print(f"Alert: {'ENABLED' if self.alert_enabled else 'DISABLED'}")
        print("Press Ctrl+C to stop\n")
        
        start_time = time.time()
        
        try:
            while True:
                self.detect_motion()
                stats = self.get_stats()
                
                # Display status
                rssi = stats['current_rssi'] or "N/A"
                status = "🚨 MOTION" if stats['current_status'] == 'MOTION' else "✓ IDLE"
                variance = stats.get('signal_variance', 0)
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"RSSI: {rssi:>4} dBm | "
                      f"Var: {variance:>6.2f} | "
                      f"Events: {stats['motion_events']} | "
                      f"{status}")
                
                time.sleep(interval)
                
                # Check duration limit
                if duration and (time.time() - start_time) > duration:
                    logger.info("Duration limit reached, stopping")
                    break
        
        except KeyboardInterrupt:
            logger.info("Motion detector stopped by user")
            print("\n" + "="*60)
            print("Motion Detector Stopped")
            print("="*60)
            self._print_final_stats()
        
        finally:
            self._cleanup()
    
    def _print_final_stats(self):
        """Print final statistics"""
        stats = self.get_stats()
        print(f"\nFinal Statistics:")
        print(f"  Uptime: {stats['uptime_seconds']:.1f} seconds")
        print(f"  Motion Events: {stats['motion_events']}")
        print(f"  Final RSSI: {stats['current_rssi']} dBm")
        print(f"  Status: {stats['current_status']}")
    
    def _cleanup(self):
        """Cleanup resources"""
        if self.alert_enabled:
            try:
                import RPi.GPIO as GPIO
                GPIO.cleanup()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
        
        logger.info("Detector cleaned up")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='WiFi Motion Detector - Detect motion using WiFi signal strength'
    )
    parser.add_argument('--interface', '-i', default='wlan0',
                        help='WiFi interface (default: wlan0)')
    parser.add_argument('--threshold', '-t', type=float, default=3,
                        help='Variance threshold (default: 3)')
    parser.add_argument('--window', '-w', type=int, default=10,
                        help='Window size for analysis (default: 10)')
    parser.add_argument('--interval', type=float, default=1,
                        help='Reading interval in seconds (default: 1)')
    parser.add_argument('--duration', '-d', type=float,
                        help='Run duration in seconds (default: infinite)')
    parser.add_argument('--alert', '-a', action='store_true',
                        help='Enable GPIO buzzer alert (requires RPi)')
    parser.add_argument('--port', '-p', type=int, default=17,
                        help='GPIO port for buzzer (default: 17)')
    
    args = parser.parse_args()
    
    # Create and run detector
    detector = WiFiMotionDetector(
        interface=args.interface,
        threshold=args.threshold,
        window_size=args.window,
        alert=args.alert,
        port=args.port
    )
    
    detector.run(interval=args.interval, duration=args.duration)


if __name__ == '__main__':
    main()
