#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create an async Modbus RTU host (master) which requests or sets data on a
client device.

The RTU communication pins can be choosen freely (check MicroPython device/
port specific limitations).
The register definitions of the client as well as its connection settings like
bus address and UART communication speed can be defined by the user.
"""

# system imports
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from umodbus.asynchronous.serial import AsyncSerial as ModbusRTUMaster
from .common.rtu_host_common import IS_DOCKER_MICROPYTHON
from .common.rtu_host_common import register_definitions
from .common.rtu_host_common import slave_addr, uart_id
from .common.rtu_host_common import baudrate, rtu_pins, exit
from .common.host_tests import run_async_host_tests


async def start_rtu_host(unit_id,
                         pins,
                         baudrate,
                         uart_id,
                         **kwargs):
    """Creates an RTU host (client) and runs tests"""

    host = ModbusRTUMaster(unit_id,
                           pins=pins,
                           baudrate=baudrate,
                           uart_id=uart_id,
                           **kwargs)

    print('Requesting and updating data on RTU client at address {} with {} baud'.
          format(slave_addr, baudrate))
    print()

    if IS_DOCKER_MICROPYTHON:
        # works only with fake machine UART
        assert host._uart._is_server is False

    await run_async_host_tests(host=host,
                               slave_addr=unit_id,
                               register_definitions=register_definitions)

# create and run task
task = start_rtu_host(
    unit_id=slave_addr,
    pins=rtu_pins,          # given as tuple (TX, RX)
    baudrate=baudrate,      # optional, default 9600
    # data_bits=8,          # optional, default 8
    # stop_bits=1,          # optional, default 1
    # parity=None,          # optional, default None
    # ctrl_pin=12,          # optional, control DE/RE
    uart_id=uart_id)        # optional, default 1, see port specific docs
asyncio.run(task)

exit()
