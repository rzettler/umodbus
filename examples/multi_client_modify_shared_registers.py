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

# extend multi client example by importing from it
from examples.multi_client_example import init_tcp_server, init_rtu_server
from examples.multi_client_example import register_definitions
from examples.multi_client_example import local_ip, tcp_port
from examples.multi_client_example import slave_addr, rtu_pins
from examples.multi_client_example import baudrate, uart_id, exit
from examples.multi_client_example import sync_registers


async def update_register_definitions(register_definitions, servers):
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


async def start_all_servers(*server_tasks) -> None:
    """
    Creates a TCP and RTU server with the given parameters, and
    starts a background task that updates their EXAMPLE_IREG registers
    every 5 seconds, which should be visible to any clients that connect.
    """

    all_servers = await asyncio.gather(*server_tasks)
    sync_registers(register_definitions, *all_servers)
    background_task = update_register_definitions(register_definitions, all_servers)
    await asyncio.gather(background_task, *[server.serve_forever() for server in all_servers])


if __name__ == "__main__":
    # define arbitrary backlog of 10
    backlog = 10

    # create TCP server task
    tcp_server_task = init_tcp_server(local_ip, tcp_port, backlog)

    # create RTU server task
    rtu_server_task = init_rtu_server(addr=slave_addr,
                                      pins=rtu_pins,          # given as tuple (TX, RX)
                                      baudrate=baudrate,      # optional, default 9600
                                      # data_bits=8,          # optional, default 8
                                      # stop_bits=1,          # optional, default 1
                                      # parity=None,          # optional, default None
                                      # ctrl_pin=12,          # optional, control DE/RE
                                      uart_id=uart_id)        # optional, default 1, see port specific docs

    # combine and run tasks together
    run_servers = start_all_servers(tcp_server_task, rtu_server_task)
    asyncio.run(run_servers)

    exit()
