#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create a Modbus TCP host (master) which requests or sets data on a client
device.

The TCP port and IP address can be choosen freely. The register definitions of
the client can be defined by the user.
"""

# import modbus host classes
from umodbus.tcp import TCP as ModbusTCPMaster
from common.register_definitions import register_definitions
from common.tcp_host_common import slave_ip, slave_tcp_port, slave_addr, exit
from common.host_tests import run_sync_host_tests

# TCP Master setup
# act as host, get Modbus data via TCP from a client device
# ModbusTCPMaster can make TCP requests to a client device to get/set data
# host = ModbusTCP(
host = ModbusTCPMaster(
    slave_ip=slave_ip,
    slave_port=slave_tcp_port,
    timeout=5)              # optional, default 5

print('Requesting and updating data on TCP client at {}:{}'.
      format(slave_ip, slave_tcp_port))
print()

run_sync_host_tests(host=host,
                    slave_addr=slave_addr,
                    register_definitions=register_definitions)

exit()
