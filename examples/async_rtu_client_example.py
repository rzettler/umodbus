#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create an async Modbus RTU client (slave) which can be requested for data or
set with specific values by a host device.

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

# import modbus client classes
from umodbus.asynchronous.serial import AsyncModbusRTU as ModbusRTU
from common.register_definitions import setup_callbacks
from common.rtu_client_common import IS_DOCKER_MICROPYTHON
from common.rtu_client_common import register_definitions
from common.rtu_client_common import slave_addr, rtu_pins
from common.rtu_client_common import baudrate, uart_id, exit


async def start_rtu_server(slave_addr,
                           rtu_pins,
                           baudrate,
                           uart_id,
                           **kwargs):
    """Creates an RTU client and runs tests"""

    client = ModbusRTU(addr=slave_addr,
                       pins=rtu_pins,
                       baudrate=baudrate,
                       uart_id=uart_id,
                       **kwargs)

    if IS_DOCKER_MICROPYTHON:
        # works only with fake machine UART
        assert client._itf._uart._is_server is True

    # reset all registers back to their default value with a callback
    setup_callbacks(client, register_definitions)

    print('Setting up registers ...')
    # use the defined values of each register type provided by register_definitions
    client.setup_registers(registers=register_definitions)
    # alternatively use dummy default values (True for bool regs, 999 otherwise)
    # client.setup_registers(registers=register_definitions, use_default_vals=True)
    print('Register setup done')

    await client.serve_forever()


# create and run task
task = start_rtu_server(addr=slave_addr,
                        pins=rtu_pins,          # given as tuple (TX, RX)
                        baudrate=baudrate,      # optional, default 9600
                        # data_bits=8,          # optional, default 8
                        # stop_bits=1,          # optional, default 1
                        # parity=None,          # optional, default None
                        # ctrl_pin=12,          # optional, control DE/RE
                        uart_id=uart_id)        # optional, default 1, see port specific docs
asyncio.run(task)

exit()
