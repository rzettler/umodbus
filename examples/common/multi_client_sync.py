#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Defines the callbacks for synchronizing register definitions
for multiple async servers.

Warning: This is a workaround for the case where register
definitions are not shared. Do not use these if they are
already shared.
"""


def sync_registers(register_definitions, *servers):
    """
    Callback which synchronizes changes to registers across servers.
    Workaround since register definitions are not yet shared.
    """

    def sync_server_hregs(other_servers):
        def inner_set_hreg_cb(reg_type, address, val):
            for server in other_servers:
                server.set_hreg(address=address, value=val)
        return inner_set_hreg_cb

    def sync_server_coils(other_servers):
        def inner_set_coil_cb(reg_type, address, val):
            for server in other_servers:
                server.set_coil(address=address, value=val)
        return inner_set_coil_cb

    print('Setting up registers ...')
    for server in servers:
        other_servers = [s for s in servers if s != server]
        for register in register_definitions['HREGS']:
            register_definitions['HREGS'][register]['on_set_cb'] = sync_server_hregs(other_servers)
        for register in register_definitions['COILS']:
            register_definitions['COILS'][register]['on_set_cb'] = sync_server_coils(other_servers)

        # use the defined values of each register type provided by register_definitions
        server.setup_registers(registers=register_definitions)
        # alternatively use dummy default values (True for bool regs, 999 otherwise)
        # server.setup_registers(registers=register_definitions, use_default_vals=True)
        print('Register setup done for all servers')
