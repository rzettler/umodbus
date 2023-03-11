# system imports
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from umodbus.asynchronous.tcp import AsyncModbusTCP, AsyncTCP
from umodbus.asynchronous.serial import AsyncModbusRTU, AsyncSerial


async def start_tcp_server(host, port, backlog):
    server = AsyncModbusTCP()
    await server.bind(local_ip=host, local_port=port, max_connections=backlog)
    await server.serve_forever()


async def start_rtu_server(addr, **kwargs):
    server = AsyncModbusRTU(addr, **kwargs)
    await server.serve_forever()


async def start_tcp_client(host, port, unit_id, timeout):
    client = AsyncTCP(slave_ip=host, slave_port=port, timeout=timeout)
    await client.connect()
    if client.is_connected:
        await client.read_coils(slave_addr=unit_id,
                                starting_addr=0,
                                coil_qty=1)


async def start_rtu_client(unit_id, **kwargs):
    client = AsyncSerial(**kwargs)
    await client.read_coils(slave_addr=unit_id,
                            starting_addr=0,
                            coil_qty=1)


def run_tcp_test(host, port, backlog):
    asyncio.run(start_tcp_server(host, port, backlog))


def run_rtu_test(addr, baudrate, data_bits, stop_bits,
                 parity, pins, ctrl_pin, uart_id):
    asyncio.run(start_rtu_server(addr, baudrate, data_bits, stop_bits,
                                 parity, pins, ctrl_pin, uart_id))


def run_tcp_client_test(host, port, unit_id, timeout):
    asyncio.run(start_tcp_client(host, port, unit_id, timeout))


def run_rtu_client_test(unit_id, **kwargs):
    asyncio.run(start_rtu_client(unit_id, **kwargs))
