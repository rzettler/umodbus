#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Defines the tests for both sync and async TCP/RTU hosts.
"""


async def run_async_host_tests(host, slave_addr, register_definitions):
    """Runs tests with a Modbus host (client)"""

    try:
        import uasyncio as asyncio
    except ImportError:
        import asyncio

    # READ COILS
    while True:
        try:
            coil_address = register_definitions['COILS']['EXAMPLE_COIL']['register']
            coil_qty = register_definitions['COILS']['EXAMPLE_COIL']['len']
            coil_status = await host.read_coils(
                slave_addr=slave_addr,
                starting_addr=coil_address,
                coil_qty=coil_qty)
            print('Status of COIL {}: {}'.format(coil_address, coil_status))
            await asyncio.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    # WRITE COILS
    while True:
        try:
            new_coil_val = 0
            operation_status = await host.write_single_coil(
                slave_addr=slave_addr,
                output_address=coil_address,
                output_value=new_coil_val)
            print('Result of setting COIL {}: {}'.format(coil_address, operation_status))
            await asyncio.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    # READ COILS again
    while True:
        try:
            coil_status = await host.read_coils(
                slave_addr=slave_addr,
                starting_addr=coil_address,
                coil_qty=coil_qty)
            print('Status of COIL {}: {}'.format(coil_address, coil_status))
            await asyncio.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    print()

    # READ HREGS
    while True:
        try:
            hreg_address = register_definitions['HREGS']['EXAMPLE_HREG']['register']
            register_qty = register_definitions['HREGS']['EXAMPLE_HREG']['len']
            register_value = await host.read_holding_registers(
                slave_addr=slave_addr,
                starting_addr=hreg_address,
                register_qty=register_qty,
                signed=False)
            print('Status of HREG {}: {}'.format(hreg_address, register_value))
            await asyncio.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    # WRITE HREGS
    while True:
        try:
            new_hreg_val = 44
            operation_status = await host.write_single_register(
                slave_addr=slave_addr,
                register_address=hreg_address,
                register_value=new_hreg_val,
                signed=False)
            print('Result of setting HREG {}: {}'.format(hreg_address, operation_status))
            await asyncio.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    # READ HREGS again
    while True:
        try:
            register_value = await host.read_holding_registers(
                slave_addr=slave_addr,
                starting_addr=hreg_address,
                register_qty=register_qty,
                signed=False)
            print('Status of HREG {}: {}'.format(hreg_address, register_value))
            await asyncio.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    print()

    # READ ISTS
    while True:
        try:
            ist_address = register_definitions['ISTS']['EXAMPLE_ISTS']['register']
            input_qty = register_definitions['ISTS']['EXAMPLE_ISTS']['len']
            input_status = await host.read_discrete_inputs(
                slave_addr=slave_addr,
                starting_addr=ist_address,
                input_qty=input_qty)
            print('Status of IST {}: {}'.format(ist_address, input_status))
            await asyncio.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    print()

    # READ IREGS
    while True:
        try:
            ireg_address = register_definitions['IREGS']['EXAMPLE_IREG']['register']
            register_qty = register_definitions['IREGS']['EXAMPLE_IREG']['len']
            register_value = await host.read_input_registers(
                slave_addr=slave_addr,
                starting_addr=ireg_address,
                register_qty=register_qty,
                signed=False)
            print('Status of IREG {}: {}'.format(ireg_address, register_value))
            await asyncio.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    print()

    # reset all registers back to their default values on the client
    # WRITE COILS
    while True:
        try:
            print('Resetting register data to default values...')
            coil_address = \
                register_definitions['COILS']['RESET_REGISTER_DATA_COIL']['register']
            new_coil_val = True
            operation_status = await host.write_single_coil(
                slave_addr=slave_addr,
                output_address=coil_address,
                output_value=new_coil_val)
            print('Result of setting COIL {}: {}'.format(coil_address, operation_status))
            await asyncio.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    print()

    print("Finished requesting/setting data on client")


def run_sync_host_tests(host, slave_addr, register_definitions):
    """Runs Modbus host (client) tests for a given address"""

    import time

    # READ COILS

    while True:
        try:
            coil_address = register_definitions['COILS']['EXAMPLE_COIL']['register']
            coil_qty = register_definitions['COILS']['EXAMPLE_COIL']['len']
            coil_status = host.read_coils(
                slave_addr=slave_addr,
                starting_addr=coil_address,
                coil_qty=coil_qty)
            print('Status of COIL {}: {}'.format(coil_address, coil_status))
            time.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    # WRITE COILS
    while True:
        try:
            new_coil_val = 0
            operation_status = host.write_single_coil(
                slave_addr=slave_addr,
                output_address=coil_address,
                output_value=new_coil_val)
            print('Result of setting COIL {} to {}'.format(coil_address, operation_status))
            time.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    # READ COILS again
    while True:
        try:
            coil_status = host.read_coils(
                slave_addr=slave_addr,
                starting_addr=coil_address,
                coil_qty=coil_qty)
            print('Status of COIL {}: {}'.format(coil_address, coil_status))
            time.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    print()

    # READ HREGS
    while True:
        try:
            hreg_address = register_definitions['HREGS']['EXAMPLE_HREG']['register']
            register_qty = register_definitions['HREGS']['EXAMPLE_HREG']['len']
            register_value = host.read_holding_registers(
                slave_addr=slave_addr,
                starting_addr=hreg_address,
                register_qty=register_qty,
                signed=False)
            print('Status of HREG {}: {}'.format(hreg_address, register_value))
            time.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    # WRITE HREGS
    while True:
        try:
            new_hreg_val = 44
            operation_status = host.write_single_register(
                slave_addr=slave_addr,
                register_address=hreg_address,
                register_value=new_hreg_val,
                signed=False)
            print('Result of setting HREG {} to {}'.format(hreg_address, operation_status))
            time.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    # READ HREGS again
    while True:
        try:
            register_value = host.read_holding_registers(
                slave_addr=slave_addr,
                starting_addr=hreg_address,
                register_qty=register_qty,
                signed=False)
            print('Status of HREG {}: {}'.format(hreg_address, register_value))
            time.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    print()

    # READ ISTS
    while True:
        try:
            ist_address = register_definitions['ISTS']['EXAMPLE_ISTS']['register']
            input_qty = register_definitions['ISTS']['EXAMPLE_ISTS']['len']
            input_status = host.read_discrete_inputs(
                slave_addr=slave_addr,
                starting_addr=ist_address,
                input_qty=input_qty)
            print('Status of IST {}: {}'.format(ist_address, input_status))
            time.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    print()

    # READ IREGS
    while True:
        try:
            ireg_address = register_definitions['IREGS']['EXAMPLE_IREG']['register']
            register_qty = register_definitions['IREGS']['EXAMPLE_IREG']['len']
            register_value = host.read_input_registers(
                slave_addr=slave_addr,
                starting_addr=ireg_address,
                register_qty=register_qty,
                signed=False)
            print('Status of IREG {}: {}'.format(ireg_address, register_value))
            time.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    print()

    # reset all registers back to their default values on the client
    # WRITE COILS
    while True:
        try:
            print('Resetting register data to default values...')
            coil_address = \
                register_definitions['COILS']['RESET_REGISTER_DATA_COIL']['register']
            new_coil_val = True
            operation_status = host.write_single_coil(
                slave_addr=slave_addr,
                output_address=coil_address,
                output_value=new_coil_val)
            print('Result of setting COIL {}: {}'.format(coil_address, operation_status))
            time.sleep(1)
            break
        except OSError as err:
            print("Potential timeout error:", err)
            pass

    print()

    print("Finished requesting/setting data on client")
