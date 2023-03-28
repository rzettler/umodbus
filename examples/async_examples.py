#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# system imports
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from umodbus.asynchronous.tcp import AsyncModbusTCP, AsyncTCP
from umodbus.asynchronous.serial import AsyncModbusRTU, AsyncSerial


async def start_rtu_server(addr, **kwargs):
    server = AsyncModbusRTU(addr, **kwargs)
    await server.serve_forever()


async def start_rtu_client(unit_id, **kwargs):
    client = AsyncSerial(**kwargs)
    await client.read_coils(slave_addr=unit_id,
                            starting_addr=0,
                            coil_qty=1)


def run_rtu_test(addr, baudrate, data_bits, stop_bits,
                 parity, pins, ctrl_pin, uart_id):
    asyncio.run(start_rtu_server(addr, baudrate, data_bits, stop_bits,
                                 parity, pins, ctrl_pin, uart_id))


def run_rtu_client_test(unit_id, **kwargs):
    asyncio.run(start_rtu_client(unit_id, **kwargs))
