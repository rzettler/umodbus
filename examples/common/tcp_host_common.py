#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Auxiliary script

Defines the common imports and functions for running the host
examples for both the synchronous and asynchronous TCP hosts.
"""

# system packages
import time

IS_DOCKER_MICROPYTHON = False
try:
    import network
except ImportError:
    IS_DOCKER_MICROPYTHON = True


def exit():
    if IS_DOCKER_MICROPYTHON:
        import sys
        sys.exit(0)


# ===============================================
if IS_DOCKER_MICROPYTHON is False:
    # connect to a network
    station = network.WLAN(network.STA_IF)
    if station.active() and station.isconnected():
        station.disconnect()
        time.sleep(1)
    station.active(False)
    time.sleep(1)
    station.active(True)

    # station.connect('SSID', 'PASSWORD')
    station.connect('TP-LINK_FBFC3C', 'C1FBFC3C')
    time.sleep(1)

    while True:
        print('Waiting for WiFi connection...')
        if station.isconnected():
            print('Connected to WiFi.')
            print(station.ifconfig())
            break
        time.sleep(2)

# ===============================================
# TCP Slave setup
slave_tcp_port = 502            # port to listen to
slave_addr = 10                 # bus address of client

# set IP address of the MicroPython device acting as client (slave)
if IS_DOCKER_MICROPYTHON:
    slave_ip = '172.24.0.2'     # static Docker IP address
else:
    slave_ip = '192.168.178.69'     # IP address

"""
# alternatively the register definitions can also be loaded from a JSON file
import json

with open('registers/example.json', 'r') as file:
    register_definitions = json.load(file)
"""
