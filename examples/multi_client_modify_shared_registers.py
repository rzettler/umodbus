#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create an async Modbus TCP and RTU client (slave) which run simultaneously,
share the same register definitions, and can be requested for data or set
with specific values by a host device. A separate background task updates
the TCP and RTU client (slave) EXAMPLE_IREG input register every 5 seconds.

The register definitions of the client as well as its connection settings like
bus address and UART communication speed can be defined by the user.
"""

# system imports
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import random

# import modbus client classes
from umodbus.asynchronous.tcp import AsyncModbusTCP as ModbusTCP
from umodbus.asynchronous.serial import AsyncModbusRTU as ModbusRTU
from examples.common.register_definitions import setup_callbacks
from examples.common.tcp_client_common import register_definitions
from examples.common.tcp_client_common import local_ip, tcp_port
from examples.common.rtu_client_common import IS_DOCKER_MICROPYTHON
from examples.common.rtu_client_common import slave_addr, rtu_pins
from examples.common.rtu_client_common import baudrate, uart_id, exit
from umodbus.typing import Tuple, Dict, Any


async def start_rtu_server(slave_addr,
                           rtu_pins,
                           baudrate,
                           uart_id,
                           **kwargs) -> Tuple[ModbusRTU, asyncio.Task]:
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

    # create a task, since we want the server to run in the background but also
    # want it to be able to stop anytime we want (by manipulating the server)
    task = asyncio.create_task(client.serve_forever())

    # we can stop the task by asking the server to stop
    # but verify it's done by querying task
    return client, task


async def start_tcp_server(host, port, backlog) -> Tuple[ModbusTCP, asyncio.Task]:
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

    # create a task, since we want the server to run in the background but also
    # want it to be able to stop anytime we want (by manipulating the server)
    task = asyncio.create_task(client.serve_forever())

    # we can stop the task by asking the server to stop
    # but verify it's done by querying task
    return client, task


async def create_servers(parameters: Dict[str, Any]) -> Tuple[Tuple[ModbusTCP, ModbusRTU],
                                                              Tuple[asyncio.Task, asyncio.Task]]:
    """Creates TCP and RTU servers based on the supplied parameters."""

    # create TCP server task
    tcp_server, tcp_task = await start_tcp_server(parameters['local_ip'],
                                                  parameters['tcp_port'],
                                                  parameters['backlog'])

    # create RTU server task
    rtu_server, rtu_task = await start_rtu_server(addr=parameters['slave_addr'],
                                                  pins=parameters['rtu_pins'],            # given as tuple (TX, RX)
                                                  baudrate=parameters['baudrate'],        # optional, default 9600
                                                  # data_bits=8,                          # optional, default 8
                                                  # stop_bits=1,                          # optional, default 1
                                                  # parity=None,                          # optional, default None
                                                  # ctrl_pin=12,                          # optional, control DE/RE
                                                  uart_id=parameters['uart_id'])          # optional, default 1, see port specific docs

    # combine both tasks
    return (tcp_server, rtu_server), (tcp_task, rtu_task)


async def update_register_definitions(register_definitions, *servers):
    """
    Updates the EXAMPLE_IREG register every 5 seconds
    to a random value for the given servers.
    """

    IREG = register_definitions['IREGS']['EXAMPLE_IREG']
    address = IREG['register']
    while True:
        value = random.randrange(1, 1000)
        print("Updating value to: ", value)
        for server in servers:
            curr_values = server.get_ireg(address)
            if isinstance(curr_values, list):
                curr_values[1] = value
            else:
                curr_values = value
            server.set_ireg(address=address, value=curr_values)

        await asyncio.sleep(5)


async def start_servers(params) -> None:
    """
    Creates a TCP and RTU server with the given parameters, and
    starts a background task that updates their EXAMPLE_IREG registers
    every 5 seconds, which should be visible to any clients that connect.
    """

    (tcp_server, rtu_server), (tcp_task, rtu_task) = await create_servers(params)

    """
    # settings for server can be loaded from a json file like so
    import json

    with open('registers/example.json', 'r') as file:
        new_params = json.load(file)

    # but for now, just look up parameters defined directly in code
    """

    background_task = update_register_definitions(register_definitions,
                                                  tcp_server, rtu_server)

    await asyncio.gather(tcp_task, rtu_task, background_task)

params = {
    "local_ip": local_ip,
    "tcp_port": tcp_port,
    "backlog": 10,
    "slave_addr": slave_addr,
    "rtu_pins": rtu_pins,
    "baudrate": baudrate,
    "uart_id": uart_id
}

asyncio.run(start_servers(params=params))

exit()
