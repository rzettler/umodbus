#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Defines the common registers for all examples, as well as the
callbacks that can be used when setting up the various clients.
"""


def my_coil_set_cb(reg_type, address, val):
    print('my_coil_set_cb, called on setting {} at {} to: {}'.
          format(reg_type, address, val))


def my_coil_get_cb(reg_type, address, val):
    print('my_coil_get_cb, called on getting {} at {}, currently: {}'.
          format(reg_type, address, val))


def my_holding_register_set_cb(reg_type, address, val):
    print('my_hr_set_sb, called on setting {} at {} to: {}'.
          format(reg_type, address, val))


def my_holding_register_get_cb(reg_type, address, val):
    print('my_hr_get_cb, called on getting {} at {}, currently: {}'.
          format(reg_type, address, val))


def my_discrete_inputs_register_get_cb(reg_type, address, val):
    print('my_di_get_cb, called on getting {} at {}, currently: {}'.
          format(reg_type, address, val))


def setup_callbacks(client, register_definitions):
    """
    Sets up all the callbacks for the register definitions, including
    those which require references to the client and the register
    definitions themselves. Done to avoid use of `global`s as this
    causes errors when defining the functions before the client(s).
    """

    def reset_data_registers_cb(reg_type, address, val):
        print('Resetting register data to default values ...')
        client.setup_registers(registers=register_definitions)
        print('Default values restored')

    def my_inputs_register_get_cb(reg_type, address, val):
        print('my_ir_get_cb, called on getting {} at {}, currently: {}'.
              format(reg_type, address, val))

        # any operation should be as short as possible to avoid response timeouts
        new_val = val[0] + 1

        # It would be also possible to read the latest ADC value at this time
        # adc = machine.ADC(12)     # check MicroPython port specific syntax
        # new_val = adc.read()

        client.set_ireg(address=address, value=new_val)
        print('Incremented current value by +1 before sending response')

    def my_holding_register_pre_set_cb(reg_type, address, val):
        print('Custom callback, called on setting {} at {} to: {}'.
              format(reg_type, address, val))

        return val not in range(0, 101)

    def my_tcp_connect_cb(address):
        print('my_tcp_connect_cb, called after tcp client connects '
              'with address {}'.format(address))

    def my_tcp_disconnect_cb(address):
        print('my_tcp_disconnect_cb, called just before tcp client disconnects '
              'with address {}'.format(address))

    # reset all registers back to their default value with a callback
    register_definitions['COILS']['RESET_REGISTER_DATA_COIL']['on_set_cb'] = \
        reset_data_registers_cb
    # input registers support only get callbacks as they can't be set
    # externally
    register_definitions['IREGS']['EXAMPLE_IREG']['on_get_cb'] = \
        my_inputs_register_get_cb

    # add callbacks for different Modbus functions
    # each register can have a different callback
    # coils and holding register support callbacks for set and get
    # as well as before-set - but before-set can only be specified
    # in register_definitions, not dynamically as it is an "extra"
    # callback
    register_definitions['HREGS']['EXAMPLE_HREG']['on_pre_set_cb'] = \
        my_holding_register_pre_set_cb
    register_definitions['COILS']['EXAMPLE_COIL']['on_set_cb'] = my_coil_set_cb
    register_definitions['COILS']['EXAMPLE_COIL']['on_get_cb'] = my_coil_get_cb
    register_definitions['HREGS']['EXAMPLE_HREG']['on_set_cb'] = \
        my_holding_register_set_cb
    register_definitions['HREGS']['EXAMPLE_HREG']['on_get_cb'] = \
        my_holding_register_get_cb
    # discrete inputs and input registers support only get callbacks as they can't
    # be set externally
    register_definitions['ISTS']['EXAMPLE_ISTS']['on_get_cb'] = \
        my_discrete_inputs_register_get_cb

    register_definitions['META'] = {
        'on_connect_cb': my_tcp_connect_cb,
        'on_disconnect_cb': my_tcp_disconnect_cb
    }


register_definitions = {
    "COILS": {
        "RESET_REGISTER_DATA_COIL": {
            "register": 42,
            "len": 1,
            "val": 0
        },
        "EXAMPLE_COIL": {
            "register": 123,
            "len": 1,
            "val": 1
        }
    },
    "HREGS": {
        "EXAMPLE_HREG": {
            "register": 93,
            "len": 1,
            "val": 19
        }
    },
    "ISTS": {
        "EXAMPLE_ISTS": {
            "register": 67,
            "len": 1,
            "val": 0
        }
    },
    "IREGS": {
        "EXAMPLE_IREG": {
            "register": 10,
            "len": 1,
            "val": 60001
        }
    }
}
