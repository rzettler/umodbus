#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create an asynchronous Modbus TCP host (master) which requests or sets data on a client
device.

The TCP port and IP address can be choosen freely. The register definitions of
the client can be defined by the user.
"""

# system packages
import time
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

# import modbus host classes
from umodbus.asynchronous.tcp import AsyncTCP as ModbusTCPMaster
from .tcp_host_common import register_definitions, slave_ip
from .tcp_host_common import slave_tcp_port, slave_addr, exit


async def run_tests(host, slave_addr):
    """Runs tests with a Modbus host (client)"""

    # READ COILS
    coil_address = register_definitions['COILS']['EXAMPLE_COIL']['register']
    coil_qty = register_definitions['COILS']['EXAMPLE_COIL']['len']
    coil_status = await host.read_coils(
        slave_addr=slave_addr,
        starting_addr=coil_address,
        coil_qty=coil_qty)
    print('Status of COIL {}: {}'.format(coil_address, coil_status))
    time.sleep(1)

    # WRITE COILS
    new_coil_val = 0
    operation_status = await host.write_single_coil(
        slave_addr=slave_addr,
        output_address=coil_address,
        output_value=new_coil_val)
    print('Result of setting COIL {}: {}'.format(coil_address, operation_status))
    time.sleep(1)

    # READ COILS again
    coil_status = await host.read_coils(
        slave_addr=slave_addr,
        starting_addr=coil_address,
        coil_qty=coil_qty)
    print('Status of COIL {}: {}'.format(coil_address, coil_status))
    time.sleep(1)

    print()

    # READ HREGS
    hreg_address = register_definitions['HREGS']['EXAMPLE_HREG']['register']
    register_qty = register_definitions['HREGS']['EXAMPLE_HREG']['len']
    register_value = await host.read_holding_registers(
        slave_addr=slave_addr,
        starting_addr=hreg_address,
        register_qty=register_qty,
        signed=False)
    print('Status of HREG {}: {}'.format(hreg_address, register_value))
    time.sleep(1)

    # WRITE HREGS
    new_hreg_val = 44
    operation_status = await host.write_single_register(
        slave_addr=slave_addr,
        register_address=hreg_address,
        register_value=new_hreg_val,
        signed=False)
    print('Result of setting HREG {}: {}'.format(hreg_address, operation_status))
    time.sleep(1)

    # READ HREGS again
    register_value = await host.read_holding_registers(
        slave_addr=slave_addr,
        starting_addr=hreg_address,
        register_qty=register_qty,
        signed=False)
    print('Status of HREG {}: {}'.format(hreg_address, register_value))
    time.sleep(1)

    print()

    # READ ISTS
    ist_address = register_definitions['ISTS']['EXAMPLE_ISTS']['register']
    input_qty = register_definitions['ISTS']['EXAMPLE_ISTS']['len']
    input_status = await host.read_discrete_inputs(
        slave_addr=slave_addr,
        starting_addr=ist_address,
        input_qty=input_qty)
    print('Status of IST {}: {}'.format(ist_address, input_status))
    time.sleep(1)

    print()

    # READ IREGS
    ireg_address = register_definitions['IREGS']['EXAMPLE_IREG']['register']
    register_qty = register_definitions['IREGS']['EXAMPLE_IREG']['len']
    register_value = await host.read_input_registers(
        slave_addr=slave_addr,
        starting_addr=ireg_address,
        register_qty=register_qty,
        signed=False)
    print('Status of IREG {}: {}'.format(ireg_address, register_value))
    time.sleep(1)

    print()

    # reset all registers back to their default values on the client
    # WRITE COILS
    print('Resetting register data to default values...')
    coil_address = \
        register_definitions['COILS']['RESET_REGISTER_DATA_COIL']['register']
    new_coil_val = True
    operation_status = await host.write_single_coil(
        slave_addr=slave_addr,
        output_address=coil_address,
        output_value=new_coil_val)
    print('Result of setting COIL {}: {}'.format(coil_address, operation_status))
    time.sleep(1)

    print()

    print("Finished requesting/setting data on client")


async def start_tcp_client(host, port, unit_id, timeout):
    # TCP Master setup
    # act as host, get Modbus data via TCP from a client device
    # ModbusTCPMaster can make TCP requests to a client device to get/set data
    client = ModbusTCPMaster(
        slave_ip=host,
        slave_port=port,
        timeout=timeout)

    # unlike synchronous client, need to call connect() here
    await client.connect()
    if client.is_connected:
        print('Requesting and updating data on TCP client at {}:{}'.
              format(host, port))
        print()

        await run_tests(client, unit_id)


# create and run task
task = start_tcp_client(host=slave_ip,
                        port=slave_tcp_port,
                        unit_id=slave_addr,
                        timeout=5)
asyncio.run(task)

exit()
