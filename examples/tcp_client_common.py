#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Auxiliary script

Defines the common imports and functions for running the client
examples for both the synchronous and asynchronous versions.
"""

IS_DOCKER_MICROPYTHON = False
try:
    import network
except ImportError:
    IS_DOCKER_MICROPYTHON = True
    import json


def my_coil_set_cb(reg_type, address, val):
    print('Custom callback, called on setting {} at {} to: {}'.
          format(reg_type, address, val))


def my_coil_get_cb(reg_type, address, val):
    print('Custom callback, called on getting {} at {}, currently: {}'.
          format(reg_type, address, val))


def my_holding_register_set_cb(reg_type, address, val):
    print('Custom callback, called on setting {} at {} to: {}'.
          format(reg_type, address, val))


def my_holding_register_get_cb(reg_type, address, val):
    print('Custom callback, called on getting {} at {}, currently: {}'.
          format(reg_type, address, val))


def my_discrete_inputs_register_get_cb(reg_type, address, val):
    print('Custom callback, called on getting {} at {}, currently: {}'.
          format(reg_type, address, val))


def my_inputs_register_get_cb(reg_type, address, val):
    # usage of global isn't great, but okay for an example
    global client

    print('Custom callback, called on getting {} at {}, currently: {}'.
          format(reg_type, address, val))

    # any operation should be as short as possible to avoid response timeouts
    new_val = val[0] + 1

    # It would be also possible to read the latest ADC value at this time
    # adc = machine.ADC(12)     # check MicroPython port specific syntax
    # new_val = adc.read()

    client.set_ireg(address=address, value=new_val)
    print('Incremented current value by +1 before sending response')


def reset_data_registers_cb(reg_type, address, val):
    # usage of global isn't great, but okay for an example
    global client
    global register_definitions

    print('Resetting register data to default values ...')
    client.setup_registers(registers=register_definitions)
    print('Default values restored')


# commond slave register setup, to be used with the Master example above
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

# alternatively the register definitions can also be loaded from a JSON file
# this is always done if Docker is used for testing purpose in order to keep
# the client registers in sync with the test registers
if IS_DOCKER_MICROPYTHON:
    with open('registers/example.json', 'r') as file:
        register_definitions = json.load(file)

# add callbacks for different Modbus functions
# each register can have a different callback
# coils and holding register support callbacks for set and get
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
register_definitions['IREGS']['EXAMPLE_IREG']['on_get_cb'] = \
    my_inputs_register_get_cb

# reset all registers back to their default value with a callback
register_definitions['COILS']['RESET_REGISTER_DATA_COIL']['on_set_cb'] = \
    reset_data_registers_cb

# ===============================================
if IS_DOCKER_MICROPYTHON is False:
    # connect to a network
    station = network.WLAN(network.STA_IF)
    if station.active() and station.isconnected():
        station.disconnect()
        time.sleep(1)
    station.active(False)
    time.sleep(1)
    station.active(True)

    # station.connect('SSID', 'PASSWORD')
    station.connect('TP-LINK_FBFC3C', 'C1FBFC3C')
    time.sleep(1)

    while True:
        print('Waiting for WiFi connection...')
        if station.isconnected():
            print('Connected to WiFi.')
            print(station.ifconfig())
            break
        time.sleep(2)

# ===============================================
# TCP Slave setup
tcp_port = 502              # port to listen to

if IS_DOCKER_MICROPYTHON:
    local_ip = '172.24.0.2'     # static Docker IP address
else:
    # set IP address of the MicroPython device explicitly
    # local_ip = '192.168.4.1'    # IP address
    # or get it from the system after a connection to the network has been made
    local_ip = station.ifconfig()[0]
