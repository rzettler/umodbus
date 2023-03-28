#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create a Modbus TCP client (slave) which can be requested for data or set with
specific values by a host device.

The TCP port and IP address can be choosen freely. The register definitions of
the client can be defined by the user.
"""

# system packages
import time

# import modbus client classes
from umodbus.tcp import ModbusTCP

# import relevant auxiliary script variables
from .tcp_client_common import local_ip, tcp_port, register_definitions

# ModbusTCP can get TCP requests from a host device to provide/set data
client = ModbusTCP()

# check whether client has been bound to an IP and port
is_bound = client.get_bound_status()
if not is_bound:
    client.bind(local_ip=local_ip, local_port=tcp_port)

print('Setting up registers ...')
# use the defined values of each register type provided by register_definitions
client.setup_registers(registers=register_definitions)
# alternatively use dummy default values (True for bool regs, 999 otherwise)
# client.setup_registers(registers=register_definitions, use_default_vals=True)
print('Register setup done')

print('Serving as TCP client on {}:{}'.format(local_ip, tcp_port))

while True:
    try:
        result = client.process()
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping TCP client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))

print("Finished providing/accepting data as client")
