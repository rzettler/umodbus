#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Auxiliary script

Defines the common imports and functions for running the client
examples for both the synchronous and asynchronous TCP clients.
"""

import time

IS_DOCKER_MICROPYTHON = False
try:
    import network
except ImportError:
    IS_DOCKER_MICROPYTHON = True

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
tcp_port = 502              # port to listen to

if IS_DOCKER_MICROPYTHON:
    local_ip = '172.24.0.2'     # static Docker IP address
else:
    # set IP address of the MicroPython device explicitly
    # local_ip = '192.168.4.1'    # IP address
    # or get it from the system after a connection to the network has been made
    local_ip = station.ifconfig()[0]
