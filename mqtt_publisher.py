#!/usr/bin/env python3
"""
MQTT Publisher for WiFi Motion Detector
Publishes motion events to MQTT broker
"""

import json
import logging
import time
from detector import WiFiMotionDetector
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MQTTMotionDetector:
    """WiFi Motion Detector with MQTT integration"""
    
    def __init__(self, mqtt_broker, mqtt_port=1883, mqtt_topic='home/motion', 
                 interface='wlan0', threshold=3):
        """
        Initialize MQTT Motion Detector
        
        Args:
            mqtt_broker: MQTT broker address
            mqtt_port: MQTT broker port
            mqtt_topic: Topic to publish to
            interface: WiFi interface
            threshold: Motion detection threshold
        """
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        
        # Initialize detector
        self.detector = WiFiMotionDetector(
            interface=interface,
            threshold=threshold
        )
        
        # Initialize MQTT
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        
        self.last_motion_state = None
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connect callback"""
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.mqtt_broker}")
            client.publish(f"{self.mqtt_topic}/status", "online", retain=True)
        else:
            logger.error(f"MQTT connection failed with code {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """MQTT disconnect callback"""
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnection (code {rc})")
        else:
            logger.info("Disconnected from MQTT broker")
    
    def on_publish(self, client, userdata, mid):
        """MQTT publish callback"""
        logger.debug(f"Message published (mid: {mid})")
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
    
    def publish_motion(self, motion_detected):
        """Publish motion event to MQTT"""
        payload = {
            'motion': motion_detected,
            'timestamp': time.time(),
            'stats': self.detector.get_stats()
        }
        
        self.client.publish(
            f"{self.mqtt_topic}/motion",
            json.dumps(payload),
            qos=1
        )
    
    def run(self, interval=1, duration=None):
        """Run detector with MQTT publishing"""
        logger.info("Starting MQTT Motion Detector")
        self.connect()
        
        start_time = time.time()
        
        try:
            while True:
                motion = self.detector.detect_motion()
                
                # Publish on state change
                if motion != self.last_motion_state:
                    self.publish_motion(motion)
                    self.last_motion_state = motion
                    
                    status = "MOTION DETECTED" if motion else "Motion stopped"
                    logger.info(status)
                
                time.sleep(interval)
                
                if duration and (time.time() - start_time) > duration:
                    break
        
        except KeyboardInterrupt:
            logger.info("Stopping MQTT Motion Detector")
        
        finally:
            self.disconnect()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='MQTT Motion Detector')
    parser.add_argument('--broker', default='localhost',
                        help='MQTT broker address')
    parser.add_argument('--port', type=int, default=1883,
                        help='MQTT broker port')
    parser.add_argument('--topic', default='home/motion',
                        help='MQTT topic')
    parser.add_argument('--interface', default='wlan0',
                        help='WiFi interface')
    parser.add_argument('--threshold', type=float, default=3,
                        help='Motion threshold')
    
    args = parser.parse_args()
    
    mqtt_detector = MQTTMotionDetector(
        mqtt_broker=args.broker,
        mqtt_port=args.port,
        mqtt_topic=args.topic,
        interface=args.interface,
        threshold=args.threshold
    )
    
    mqtt_detector.run()
