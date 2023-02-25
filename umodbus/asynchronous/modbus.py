#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Modbus register abstraction class

Used to add, remove, set and get values or states of a register or coil.
Additional helper properties and functions like getters for changed registers
are available as well.

This class is inherited by the Modbus client implementations
:py:class:`umodbus.serial.ModbusRTU` and :py:class:`umodbus.tcp.ModbusTCP`
"""

# system packages
from ..sys_imports import List, Optional, Union

# custom packages
from .common import AsyncRequest
from ..modbus import Modbus


class AsyncModbus(Modbus):
    """Modbus register abstraction."""

    def __init__(self,
                 # in quotes because of circular import errors
                 itf: Union["AsyncTCPServer", "AsyncRTUServer"],  # noqa: F821
                 addr_list: Optional[List[int]] = None):
        super().__init__(itf, addr_list)
        self._itf.set_params(addr_list=addr_list, req_handler=self.process)

    async def process(self, request: Optional[AsyncRequest] = None) -> None:
        """@see Modbus.process"""

        result = super().process(request)
        if result is not None:
            await result

    async def _process_read_access(self,
                                   request: AsyncRequest,
                                   reg_type: str) -> None:
        """@see Modbus._process_read_access"""

        task = super()._process_read_access(request, reg_type)
        if task is not None:
            await task

    async def _process_write_access(self,
                                    request: AsyncRequest,
                                    reg_type: str) -> None:
        """@see Modbus._process_write_access"""

        task = super()._process_write_access(request, reg_type)
        if task is not None:
            await task
