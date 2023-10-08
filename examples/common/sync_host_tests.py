#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Defines the tests for both sync TCP/RTU hosts.
"""


def _read_coils_test(host, slave_addr, register_definitions, sleep_fn, **kwargs):
    coil_address = register_definitions['COILS']['EXAMPLE_COIL']['register']
    coil_qty = register_definitions['COILS']['EXAMPLE_COIL']['len']
    coil_status = host.read_coils(
        slave_addr=slave_addr,
        starting_addr=coil_address,
        coil_qty=coil_qty)
    print('Status of COIL {}: {}'.format(coil_address, coil_status))
    sleep_fn(1)
    return {
        "coil_address": coil_address,
        "coil_qty": coil_qty
    }


def _write_coils_test(host, slave_addr, register_definitions, sleep_fn, **kwargs):
    new_coil_val = 0
    coil_address = kwargs["coil_address"]
    operation_status = host.write_single_coil(
        slave_addr=slave_addr,
        output_address=coil_address,
        output_value=new_coil_val)
    print('Result of setting COIL {}: {}'.format(coil_address, operation_status))
    sleep_fn(1)

    return {"new_coil_val": new_coil_val}


def _read_hregs_test(host, slave_addr, register_definitions, sleep_fn, **kwargs):
    hreg_address = register_definitions['HREGS']['EXAMPLE_HREG']['register']
    register_qty = register_definitions['HREGS']['EXAMPLE_HREG']['len']
    register_value = host.read_holding_registers(
        slave_addr=slave_addr,
        starting_addr=hreg_address,
        register_qty=register_qty,
        signed=False)
    print('Status of HREG {}: {}'.format(hreg_address, register_value))
    sleep_fn(1)

    return {"hreg_address": hreg_address}


def _write_hregs_test(host, slave_addr, register_definitions, sleep_fn, **kwargs):
    new_hreg_val = 44
    hreg_address = kwargs["hreg_address"]
    operation_status = host.write_single_register(
        slave_addr=slave_addr,
        register_address=hreg_address,
        register_value=new_hreg_val,
        signed=False)
    print('Result of setting HREG {}: {}'.format(hreg_address, operation_status))
    sleep_fn(1)


def _write_hregs_beyond_limits_test(host, slave_addr, register_definitions, sleep_fn, **kwargs):
    # try to set value outside specified range of [0, 101]
    # in register_definitions on_pre_set_cb callback
    new_hreg_val = 500
    hreg_address = kwargs["hreg_address"]
    operation_status = host.write_single_register(
        slave_addr=slave_addr,
        register_address=hreg_address,
        register_value=new_hreg_val,
        signed=False)
    # should be error: illegal data value
    print('Result of setting HREG {}: {}'.format(hreg_address, operation_status))
    sleep_fn(1)


def _read_ists_test(host, slave_addr, register_definitions, sleep_fn, **kwargs):
    ist_address = register_definitions['ISTS']['EXAMPLE_ISTS']['register']
    input_qty = register_definitions['ISTS']['EXAMPLE_ISTS']['len']
    input_status = host.read_discrete_inputs(
        slave_addr=slave_addr,
        starting_addr=ist_address,
        input_qty=input_qty)
    print('Status of IST {}: {}'.format(ist_address, input_status))
    sleep_fn(1)


def _read_iregs_test(host, slave_addr, register_definitions, sleep_fn, **kwargs):
    ireg_address = register_definitions['IREGS']['EXAMPLE_IREG']['register']
    register_qty = register_definitions['IREGS']['EXAMPLE_IREG']['len']
    register_value = host.read_input_registers(
        slave_addr=slave_addr,
        starting_addr=ireg_address,
        register_qty=register_qty,
        signed=False)
    print('Status of IREG {}: {}'.format(ireg_address, register_value))
    sleep_fn(1)


def _reset_registers_test(host, slave_addr, register_definitions, sleep_fn, **kwargs):
    print('Resetting register data to default values...')
    coil_address = \
        register_definitions['COILS']['RESET_REGISTER_DATA_COIL']['register']
    new_coil_val = True
    operation_status = host.write_single_coil(
        slave_addr=slave_addr,
        output_address=coil_address,
        output_value=new_coil_val)
    print('Result of setting COIL {}: {}'.format(coil_address, operation_status))
    sleep_fn(1)


def run_host_tests(host, slave_addr, register_definitions, exit_on_timeout=False):
    """Runs tests with a Modbus host (client)"""

    import time

    callbacks = [
        _read_coils_test, _write_coils_test, _read_coils_test,
        _read_hregs_test, _write_hregs_test, _read_hregs_test,
        _write_hregs_beyond_limits_test, _read_hregs_test,
        _read_ists_test, _read_iregs_test, _reset_registers_test
    ]

    test_vars = {}
    current_callback_idx = 0
    # run test pipeline
    while current_callback_idx < len(callbacks):
        try:
            current_callback = callbacks[current_callback_idx]
            new_vars = current_callback(
                host=host, slave_addr=slave_addr, register_definitions=register_definitions,
                sleep_fn=time.sleep, **test_vars)

            # test succeeded, move on to the next
            if new_vars is not None:
                test_vars.update(new_vars)
            current_callback_idx += 1
            print()
        except OSError as err:
            print("Potential timeout error:", err)
            if exit_on_timeout:
                break

    print("Finished requesting/setting data on client")
