#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create a Modbus RTU host (master) which requests or sets data on a client
device.

The RTU communication pins can be choosen freely (check MicroPython device/
port specific limitations).
The register definitions of the client as well as its connection settings like
bus address and UART communication speed can be defined by the user.
"""

# import modbus host classes
from umodbus.serial import Serial as ModbusRTUMaster
from common.rtu_host_common import IS_DOCKER_MICROPYTHON
from common.rtu_host_common import register_definitions
from common.rtu_host_common import rtu_pins, baudrate
from common.rtu_host_common import slave_addr, uart_id, exit
from common.host_tests import run_sync_host_tests

host = ModbusRTUMaster(
    pins=rtu_pins,          # given as tuple (TX, RX)
    baudrate=baudrate,      # optional, default 9600
    # data_bits=8,          # optional, default 8
    # stop_bits=1,          # optional, default 1
    # parity=None,          # optional, default None
    # ctrl_pin=12,          # optional, control DE/RE
    uart_id=uart_id         # optional, default 1, see port specific docs
)

if IS_DOCKER_MICROPYTHON:
    # works only with fake machine UART
    assert host._uart._is_server is False


"""
# alternatively the register definitions can also be loaded from a JSON file
import json

with open('registers/example.json', 'r') as file:
    register_definitions = json.load(file)
"""

print('Requesting and updating data on RTU client at address {} with {} baud'.
      format(slave_addr, baudrate))
print()

run_sync_host_tests(host=host,
                    slave_addr=slave_addr,
                    register_definitions=register_definitions)

exit()
