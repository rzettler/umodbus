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
from examples.common.register_definitions import register_definitions
from examples.common.rtu_host_common import IS_DOCKER_MICROPYTHON
from examples.common.rtu_host_common import slave_addr, uart_id, read_timeout
from examples.common.rtu_host_common import baudrate, rtu_pins, exit
from examples.common.async_host_tests import run_host_tests


async def start_rtu_host(rtu_pins,
                         baudrate=9600,
                         data_bits=8,
                         stop_bits=1,
                         parity=None,
                         ctrl_pin=12,
                         uart_id=1,
                         read_timeout=120,
                         **extra_args):
    """Creates an RTU host (client) and runs tests"""

    host = ModbusRTUMaster(
        pins=rtu_pins,                  # given as tuple (TX, RX)
        baudrate=baudrate,              # optional, default 9600
        data_bits=data_bits,            # optional, default 8
        stop_bits=stop_bits,            # optional, default 1
        parity=parity,                  # optional, default None
        ctrl_pin=ctrl_pin,              # optional, control DE/RE
        uart_id=uart_id,                # optional, default 1, see port specific docs
        read_timeout=read_timeout,      # optional, default 120
        **extra_args                    # untested args: timeout_char (default 2)
    )

    print('Requesting and updating data on RTU client at address {} with {} baud'.
          format(slave_addr, baudrate))
    print()

    if IS_DOCKER_MICROPYTHON:
        # works only with fake machine UART
        assert host._uart._is_server is False

    await run_host_tests(host=host,
                         slave_addr=slave_addr,
                         register_definitions=register_definitions)

# create and run task
task = start_rtu_host(
    rtu_pins=rtu_pins,              # given as tuple (TX, RX)
    baudrate=baudrate,              # optional, default 9600
    # data_bits=8,                  # optional, default 8
    # stop_bits=1,                  # optional, default 1
    # parity=None,                  # optional, default None
    # ctrl_pin=12,                  # optional, control DE/RE
    uart_id=uart_id,                # optional, default 1, see port specific docs
    read_timeout=read_timeout,      # optional, default 120
    # timeout_char=2                # untested, default 2 (ms)
)
asyncio.run(task)

exit()
