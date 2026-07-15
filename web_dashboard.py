#!/usr/bin/env python3
"""
Web Dashboard for WiFi Motion Detector
Flask-based web interface for monitoring motion detection
"""

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from detector import WiFiMotionDetector
import threading
import time
import json
import logging
from datetime import datetime
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global detector instance
detector = None
detector_thread = None
motion_history = deque(maxlen=100)

class DetectorManager:
    """Manages detector lifecycle"""
    def __init__(self):
        self.detector = None
        self.running = False
        self.thread = None
    
    def start(self, interface='wlan0', threshold=3, window_size=10):
        """Start the motion detector"""
        if self.running:
            return False
        
        try:
            self.detector = WiFiMotionDetector(
                interface=interface,
                threshold=threshold,
                window_size=window_size
            )
            self.running = True
            self.thread = threading.Thread(target=self._run_detector, daemon=True)
            self.thread.start()
            logger.info("Detector started")
            return True
        except Exception as e:
            logger.error(f"Failed to start detector: {e}")
            return False
    
    def stop(self):
        """Stop the motion detector"""
        self.running = False
        if self.detector:
            self.detector._cleanup()
        logger.info("Detector stopped")
    
    def _run_detector(self):
        """Run detector loop"""
        while self.running:
            try:
                motion = self.detector.detect_motion()
                
                # Record motion events
                if motion:
                    motion_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'motion': True
                    })
                
                time.sleep(1)
            except Exception as e:
                logger.error(f"Detector error: {e}")
                time.sleep(1)
    
    def get_status(self):
        """Get current detector status"""
        if not self.detector:
            return None
        return self.detector.get_stats()
    
    def get_motion_history(self):
        """Get motion event history"""
        return list(motion_history)

# Initialize manager
manager = DetectorManager()

# ============== Routes ==============

@app.route('/')
def index():
    """Serve main dashboard"""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_detector():
    """Start motion detection"""
    data = request.json or {}
    interface = data.get('interface', 'wlan0')
    threshold = data.get('threshold', 3)
    window_size = data.get('window_size', 10)
    
    success = manager.start(interface, threshold, window_size)
    return jsonify({
        'success': success,
        'message': 'Detector started' if success else 'Failed to start detector'
    })

@app.route('/api/stop', methods=['POST'])
def stop_detector():
    """Stop motion detection"""
    manager.stop()
    return jsonify({'success': True, 'message': 'Detector stopped'})

@app.route('/api/status')
def get_status():
    """Get current detector status"""
    status = manager.get_status()
    if status:
        return jsonify(status)
    return jsonify({'error': 'Detector not running'}), 400

@app.route('/api/history')
def get_history():
    """Get motion event history"""
    history = manager.get_motion_history()
    return jsonify({
        'history': history,
        'count': len(history)
    })

@app.route('/api/config')
def get_config():
    """Get detector configuration"""
    if not manager.detector:
        return jsonify({'error': 'Detector not running'}), 400
    
    return jsonify({
        'interface': manager.detector.interface,
        'threshold': manager.detector.threshold,
        'window_size': manager.detector.window_size,
        'running': manager.running
    })

@app.route('/api/config', methods=['PUT'])
def update_config():
    """Update detector configuration"""
    data = request.json or {}
    
    if not manager.detector:
        return jsonify({'error': 'Detector not running'}), 400
    
    if 'threshold' in data:
        manager.detector.threshold = data['threshold']
    
    if 'window_size' in data:
        manager.detector.window_size = data['window_size']
    
    return jsonify({
        'success': True,
        'message': 'Configuration updated'
    })

@app.route('/api/reset', methods=['POST'])
def reset_detector():
    """Reset detector statistics"""
    if manager.detector:
        manager.detector.motion_count = 0
        manager.detector.rssi_history.clear()
        motion_history.clear()
        return jsonify({'success': True, 'message': 'Statistics reset'})
    return jsonify({'error': 'Detector not running'}), 400

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'detector_running': manager.running,
        'timestamp': datetime.now().isoformat()
    })

# ============== Error Handlers ==============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='WiFi Motion Detector Web Dashboard')
    parser.add_argument('--host', default='0.0.0.0', help='Web server host')
    parser.add_argument('--port', type=int, default=5000, help='Web server port')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("WiFi Motion Detector Web Dashboard")
    print("="*60)
    print(f"Server running at http://{args.host}:{args.port}")
    print(f"Access from phone: http://<your-ip>:{args.port}")
    print("="*60 + "\n")
    
    app.run(host=args.host, port=args.port, debug=args.debug)
