#!/usr/bin/env python3
#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

# system packages
from ..sys_imports import struct
from ..sys_imports import List, Literal, Optional, Tuple, Union

try:
    import uasyncio as asyncio
    from machine import UART, Pin
except ImportError:
    import asyncio

# custom packages
from .. import functions, const as Const
from .common import AsyncRequest
from .modbus import Modbus


class SerialServer(AbstractServerInterface):
    def __init__(self,
                 uart_id:int = 1,
                 baudrate:int = 9600,
                 data_bits:int = 8,
                 stop_bits:int = 1,
                 parity=None,
                 pins: Tuple[int, int] = (13, 14),
                 ctrl_pin=None):
        super().__init__()
        self._uart = UART(uart_id,
                          baudrate=baudrate,
                          bits=data_bits,
                          parity=parity,
                          stop=stop_bits,
                          # timeout_chars=2,  # WiPy only
                          # pins=pins         # WiPy only
                          tx=pins[0],
                          rx=pins[1]
                          )
        self.uart_in = asyncio.StreamReader(self._uart)
        self.uart_out = asyncio.StreamWriter(self._uart, {}, reader=self.uart_in, loop=asyncio.get_running_loop())

        if baudrate <= 19200:
            # 4010us (approx. 4ms) @ 9600 baud
            self._t35chars = (3500000 * (data_bits + stop_bits + 2)) // baudrate
        else:
            self._t35chars = 1750   # 1750us (approx. 1.75ms)

        if ctrl_pin is not None:
            self._ctrlPin = Pin(ctrl_pin, mode=Pin.OUT)
        else:
            self._ctrlPin = None

    def bind(self, local_ip: str, local_port: int = 502, max_connections: int = 10) -> None:
        # TODO implement server mode for serial using 
        # StreamReader and StreamWriter which calls _handle_request()
        raise NotImplementedError("RTU in server mode not supported yet.")

    def _calculate_crc16(self, data) -> bytes:
        crc = 0xFFFF

        for char in data:
            crc = (crc >> 8) ^ Const.CRC16_TABLE[((crc) ^ char) & 0xFF]

        return struct.pack('<H', crc)

    async def _send_with(self, writer: asyncio.StreamWriter, req_tid: int, modbus_pdu: Union[bytes, memoryview], slave_addr: int) -> None:
        serial_pdu = bytearray([slave_addr]) + modbus_pdu
        crc = self._calculate_crc16(serial_pdu)
        serial_pdu.extend(crc)

        if self._ctrlPin:
            self._ctrlPin(1)

        writer.write(serial_pdu)

        if self._ctrlPin:
            await writer.drain()
            await asyncio.sleep(self._t35chars)
            self._ctrlPin(0)

    async def _uart_read_frame(self, timeout=None) -> bytes:
        # set timeout to at least twice the time between two frames in case the
        # timeout was set to zero or None
        if timeout == 0 or timeout is None:
            timeout = 2 * self._t35chars  # in milliseconds

        return await asyncio.wait_for(self.uart_in.read(), timeout=timeout)

    async def send_response(self,
                      slave_addr,
                      function_code,
                      request_register_addr,
                      request_register_qty,
                      request_data,
                      values=None,
                      signed=True) -> None:
        modbus_pdu = functions.response(function_code,
                                        request_register_addr,
                                        request_register_qty,
                                        request_data,
                                        values,
                                        signed)
        await self._send_with(self.uart_out, 0, modbus_pdu, slave_addr)

    async def send_exception_response(self,
                                slave_addr,
                                function_code,
                                exception_code):
        modbus_pdu = functions.exception_response(function_code,
                                                  exception_code)
        await self._send_with(self.uart_out, 0, modbus_pdu, slave_addr)

    async def _accept_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        return await super()._accept_request(reader, writer)

    async def get_request(self, timeout: float = 0):
        req = await self._uart_read_frame(timeout)

        if len(req) < 8 or self._unit_addr_list is None or req[0] not in self._unit_addr_list:
            return None

        req_crc = req[-Const.CRC_LENGTH:]
        req_no_crc = req[:-Const.CRC_LENGTH]
        expected_crc = self._calculate_crc16(req_no_crc)

        if (req_crc[0] != expected_crc[0]) or (req_crc[1] != expected_crc[1]):
            return None

        try:
            if self._handle_request is not None:
                await self._handle_request(Request(self, writer=self.uart_out, transaction_id=0, data=memoryview(req_no_crc)))
        except ModbusException as e:
            await self.send_exception_response(req[0],
                                               e.function_code,
                                               e.exception_code)

class Serial(SerialServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _exit_read(self, response: memoryview) -> bool:
        if response[1] >= Const.ERROR_BIAS:
            if len(response) < Const.ERROR_RESP_LEN:
                return False
        elif (Const.READ_COILS <= response[1] <= Const.READ_INPUT_REGISTER):
            expected_len = Const.RESPONSE_HDR_LENGTH + 1 + response[2] + Const.CRC_LENGTH
            if len(response) < expected_len:
                return False
        elif len(response) < Const.FIXED_RESP_LEN:
            return False

        return True

    async def _uart_read(self) -> memoryview:
        # TODO check - is this correct?
        response = memoryview(await self.uart_in.read())
        for i in range(len(response)):
            # variable length function codes may require multiple reads
            if self._exit_read(response[:i]):
                return response[:i]

        return memoryview(response)

    async def _send_receive(self, slave_id: int, modbus_pdu: memoryview, count: bool = False, wait: bool = True) -> Optional[memoryview]:
        # flush the Rx FIFO
        self.uart_in.read()
        await self._send_with(self.uart_out, 0, modbus_pdu, slave_id)
        return self._validate_resp_hdr(await self._uart_read(), 0, slave_id, modbus_pdu[0], count)

    def _validate_resp_hdr(self, response: memoryview, trans_id: int, slave_id: int, function_code: int, count: bool = False, ignore_errors: bool = False) -> memoryview:
        if len(response) == 0:
            raise OSError('no data received from slave')

        resp_crc = response[-Const.CRC_LENGTH:]
        expected_crc = self._calculate_crc16(response[0:len(response) - Const.CRC_LENGTH])

        if ((resp_crc[0] is not expected_crc[0]) or (resp_crc[1] is not expected_crc[1])):
            raise OSError('invalid response CRC')

        if (response[0] != slave_id):
            raise ValueError('wrong slave address')

        if (response[1] == (function_code + Const.ERROR_BIAS)):
            raise ValueError('slave returned exception code: {:d}'.
                             format(response[2]))

        hdr_length = (Const.RESPONSE_HDR_LENGTH + 1) if count else Const.RESPONSE_HDR_LENGTH

        return response[hdr_length:len(response) - Const.CRC_LENGTH]

    async def read_coils(self, slave_addr: int, starting_addr: int, coil_qty: int) -> List[bool]:
        modbus_pdu = functions.read_coils(starting_addr, coil_qty)

        response: Optional[memoryview] = await self._send_receive(slave_addr, memoryview(modbus_pdu), True)
        if response is not None:
            return functions.bytes_to_bool(byte_list=response,
                                             bit_qty=coil_qty)
        raise ValueError("Connection timed out")

    async def read_discrete_inputs(self, slave_addr: int, starting_addr: int, input_qty: int) -> List[bool]:
        modbus_pdu = functions.read_discrete_inputs(starting_addr, input_qty)

        response: Optional[memoryview] = await self._send_receive(slave_addr, memoryview(modbus_pdu), True)
        if response is not None:
            return functions.bytes_to_bool(byte_list=response,
                                             bit_qty=input_qty)
        raise ValueError("Connection timed out")

    async def read_holding_registers(self, slave_addr: int, starting_addr: int, register_qty: int, signed: bool = True) -> bytes:
        modbus_pdu = functions.read_holding_registers(starting_addr, register_qty)

        resp_data: Optional[memoryview] = await self._send_receive(slave_addr, memoryview(modbus_pdu), True)
        if resp_data is not None:
            return functions.to_short(resp_data, signed)
        raise ValueError("Connection timed out")

    async def read_input_registers(self, slave_addr: int, starting_addr: int, register_qty: int, signed: bool = True) -> bytes:
        modbus_pdu = functions.read_input_registers(starting_addr,
                                                    register_qty)

        resp_data: Optional[memoryview] = await self._send_receive(slave_addr, memoryview(modbus_pdu), True)
        if resp_data is not None:
            return functions.to_short(resp_data, signed)
        raise ValueError("Connection timed out")

    async def write_single_coil(self, slave_addr: int, output_address: int, output_value: Literal[0x0000, 0xFF00], wait: bool = True) -> bool:
        modbus_pdu = functions.write_single_coil(output_address, output_value)

        resp_data: Optional[memoryview] = await self._send_receive(slave_addr, memoryview(modbus_pdu), False)
        if resp_data is not None:
            return functions.validate_resp_data(resp_data,
                                                Const.WRITE_SINGLE_COIL,
                                                output_address,
                                                value=output_value,
                                                signed=False)
        raise ValueError("Connection timed out")

    async def write_single_register(self, slave_addr: int, register_address: int, register_value: int, signed: bool = True, wait: bool = True) -> bool:
        modbus_pdu = functions.write_single_register(register_address,
                                                     register_value,
                                                     signed)

        resp_data: Optional[memoryview] = await self._send_receive(slave_addr, memoryview(modbus_pdu), False)
        if resp_data is not None:
            return functions.validate_resp_data(resp_data,
                                                Const.WRITE_SINGLE_REGISTER,
                                                register_address,
                                                value=register_value,
                                                signed=signed)
        raise ValueError("Connection timed out")

    async def write_multiple_coils(self, slave_addr: int, starting_address: int, output_values: List[Literal[0, 65280]], wait: bool = True) -> bool:
        modbus_pdu = functions.write_multiple_coils(starting_address,
                                                    output_values)

        resp_data: Optional[memoryview] = await self._send_receive(slave_addr, memoryview(modbus_pdu), False)
        if resp_data is not None:
            return functions.validate_resp_data(resp_data,
                                                Const.WRITE_MULTIPLE_COILS,
                                                starting_address,
                                                quantity=len(output_values))
        raise ValueError("Connection timed out")

    async def write_multiple_registers(self, slave_addr: int, starting_address: int, register_values: List[int], signed: bool = True, wait: bool = True) -> bool:
        modbus_pdu = functions.write_multiple_registers(starting_address,
                                                        register_values,
                                                        signed)

        resp_data: Optional[memoryview] = await self._send_receive(slave_addr, memoryview(modbus_pdu), False)
        if resp_data is not None:
            return functions.validate_resp_data(resp_data,
                                                Const.WRITE_MULTIPLE_REGISTERS,
                                                starting_address,
                                                quantity=len(register_values))
        raise ValueError("Connection timed out")
    
class ModbusRTU(Modbus):
    def __init__(self,
                 addr,
                 baudrate=9600,
                 data_bits=8,
                 stop_bits=1,
                 parity=None,
                 pins=None,
                 ctrl_pin=None):
        super().__init__(
            # set itf to Serial object, addr_list to [addr]
            Serial(uart_id=1,
                   baudrate=baudrate,
                   data_bits=data_bits,
                   stop_bits=stop_bits,
                   parity=parity,
                   pins=pins,
                   ctrl_pin=ctrl_pin),
            [addr]
        )
