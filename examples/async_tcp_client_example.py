#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create an async Modbus TCP client (slave) which can be requested for data or
set with specific values by a host device.

The TCP port and IP address can be choosen freely. The register definitions of
the client can be defined by the user.
"""

# system imports
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from umodbus.asynchronous.tcp import AsyncModbusTCP as ModbusTCP
from examples.common.tcp_client_common import IS_DOCKER_MICROPYTHON
from examples.common.tcp_client_common import register_definitions
from examples.common.tcp_client_common import local_ip, tcp_port
from examples.common.register_definitions import setup_callbacks


async def start_tcp_server(host, port, backlog, register_definitions):
    client = ModbusTCP()  # TODO: rename to `server`
    await client.bind(local_ip=host, local_port=port, max_connections=backlog)

    print('Setting up registers ...')
    # setup remaining callbacks after creating client
    setup_callbacks(client, register_definitions)
    # use the defined values of each register type provided by register_definitions
    client.setup_registers(registers=register_definitions)
    # alternatively use dummy default values (True for bool regs, 999 otherwise)
    # client.setup_registers(registers=register_definitions, use_default_vals=True)
    print('Register setup done')

    print('Serving as TCP client on {}:{}'.format(local_ip, tcp_port))
    await client.serve_forever()


# alternatively the register definitions can also be loaded from a JSON file
# this is always done if Docker is used for testing purpose in order to keep
# the client registers in sync with the test registers
if IS_DOCKER_MICROPYTHON:
    import json
    with open('registers/example.json', 'r') as file:
        register_definitions = json.load(file)  # noqa: F811

# create and run task
task = start_tcp_server(host=local_ip,
                        port=tcp_port,
                        backlog=10,         # arbitrary backlog
                        register_definitions=register_definitions)
asyncio.run(task)
