#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# system imports
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from umodbus.asynchronous.tcp import AsyncModbusTCP
from .tcp_client_common import local_ip, tcp_port, register_definitions

async def start_tcp_server(host, port, backlog):
    server = AsyncModbusTCP()
    await server.bind(local_ip=host, local_port=port, max_connections=backlog)

    print('Setting up registers ...')
    # use the defined values of each register type provided by register_definitions
    server.setup_registers(registers=register_definitions)
    # alternatively use dummy default values (True for bool regs, 999 otherwise)
    # client.setup_registers(registers=register_definitions, use_default_vals=True)
    print('Register setup done')

    print('Serving as TCP client on {}:{}'.format(local_ip, tcp_port))
    await server.serve_forever()


# define arbitrary backlog of 10
backlog = 10

# create and run task
task = start_tcp_server(local_ip, tcp_port, backlog)
asyncio.run(task)
