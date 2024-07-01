#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create a Modbus RTU client (slave) which can be requested for data or set with
specific values by a host device.

The RTU communication pins can be choosen freely (check MicroPython device/
port specific limitations).
The register definitions of the client as well as its connection settings like
bus address and UART communication speed can be defined by the user.
"""

# import modbus client classes
from umodbus.serial import ModbusRTU
from examples.common.register_definitions import register_definitions, setup_callbacks
from examples.common.rtu_client_common import IS_DOCKER_MICROPYTHON
from examples.common.rtu_client_common import slave_addr, rtu_pins
from examples.common.rtu_client_common import baudrate, uart_id, exit


client = ModbusRTU(
    addr=slave_addr,        # address on bus
    pins=rtu_pins,          # given as tuple (TX, RX)
    baudrate=baudrate,      # optional, default 9600
    # data_bits=8,          # optional, default 8
    # stop_bits=1,          # optional, default 1
    # parity=None,          # optional, default None
    # ctrl_pin=12,          # optional, control DE/RE
    uart_id=uart_id         # optional, default 1, see port specific docs
)

if IS_DOCKER_MICROPYTHON:
    import json
    # works only with fake machine UART
    assert client._itf._uart._is_server is True
    with open('registers/example.json', 'r') as file:
        register_definitions = json.load(file)  # noqa: F811


# reset all registers back to their default value with a callback
setup_callbacks(client, register_definitions)

print('Setting up registers ...')
# use the defined values of each register type provided by register_definitions
client.setup_registers(registers=register_definitions)
# alternatively use dummy default values (True for bool regs, 999 otherwise)
# client.setup_registers(registers=register_definitions, use_default_vals=True)
print('Register setup done')

print('Serving as RTU client on address {} at {} baud'.
      format(slave_addr, baudrate))

while True:
    try:
        result = client.process()
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping RTU client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))
        raise

print("Finished providing/accepting data as client")

exit()
