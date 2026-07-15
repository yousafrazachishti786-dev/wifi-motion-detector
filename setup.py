#!/usr/bin/env python3
"""
Setup script for WiFi Motion Detector
"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='wifi-motion-detector',
    version='1.0.0',
    description='Motion detection using WiFi signal strength (RSSI)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='WiFi Detector Dev',
    python_requires='>=3.7',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.24.0',
        'scipy>=1.11.0',
        'requests>=2.31.0',
        'paho-mqtt>=1.6.0',
        'python-dotenv>=1.0.0',
    ],
    entry_points={
        'console_scripts': [
            'wifi-motion-detector=detector:main',
            'mqtt-motion-detector=mqtt_publisher:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
