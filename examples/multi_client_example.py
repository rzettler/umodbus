#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create an async Modbus TCP and RTU client (slave) which run simultaneously,
share the same register definitions, and can be requested for data or set
with specific values by a host device.

The TCP port and IP address, and the RTU communication pins can both be
chosen freely (check MicroPython device/port specific limitations).

The register definitions of the client as well as its connection settings like
bus address and UART communication speed can be defined by the user.
"""

# system imports
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

# import modbus client classes
from umodbus.asynchronous.tcp import AsyncModbusTCP as ModbusTCP
from umodbus.asynchronous.serial import AsyncModbusRTU as ModbusRTU
from examples.common.register_definitions import setup_callbacks
from examples.common.tcp_client_common import register_definitions
from examples.common.tcp_client_common import local_ip, tcp_port
from examples.common.rtu_client_common import IS_DOCKER_MICROPYTHON
from examples.common.rtu_client_common import slave_addr, rtu_pins
from examples.common.rtu_client_common import baudrate, uart_id, exit


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

    # start listening in background
    await client.bind()

    print('Setting up RTU registers ...')
    # use the defined values of each register type provided by register_definitions
    client.setup_registers(registers=register_definitions)
    # alternatively use dummy default values (True for bool regs, 999 otherwise)
    # client.setup_registers(registers=register_definitions, use_default_vals=True)
    print('RTU Register setup done')

    await client.serve_forever()


async def start_tcp_server(host, port, backlog):
    client = ModbusTCP()  # TODO: rename to `server`
    await client.bind(local_ip=host, local_port=port, max_connections=backlog)

    print('Setting up TCP registers ...')
    # only one server for now can have callbacks setup for it
    setup_callbacks(client, register_definitions)
    # use the defined values of each register type provided by register_definitions
    client.setup_registers(registers=register_definitions)
    # alternatively use dummy default values (True for bool regs, 999 otherwise)
    # client.setup_registers(registers=register_definitions, use_default_vals=True)
    print('TCP Register setup done')

    print('Serving as TCP client on {}:{}'.format(local_ip, tcp_port))
    await client.serve_forever()


# define arbitrary backlog of 10
backlog = 10

# create TCP server task
tcp_task = start_tcp_server(local_ip, tcp_port, backlog)

# create RTU server task
rtu_task = start_rtu_server(addr=slave_addr,
                            pins=rtu_pins,          # given as tuple (TX, RX)
                            baudrate=baudrate,      # optional, default 9600
                            # data_bits=8,          # optional, default 8
                            # stop_bits=1,          # optional, default 1
                            # parity=None,          # optional, default None
                            # ctrl_pin=12,          # optional, control DE/RE
                            uart_id=uart_id)        # optional, default 1, see port specific docs

# combine and run both tasks together
run_both_tasks = asyncio.gather(tcp_task, rtu_task)
asyncio.run(run_both_tasks)

exit()
