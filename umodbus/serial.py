#!/usr/bin/env python
#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

# system packages
from .sys_imports import struct, time, machine, UART, Pin
from .sys_imports import List, Optional, Union, Awaitable

# custom packages
from . import const as Const
from . import functions
from .common import Request, CommonModbusFunctions
from .common import ModbusException
from .modbus import Modbus


class ModbusRTU(Modbus):
    """
    Modbus RTU client class

    :param      addr:        The address of this device on the bus
    :type       addr:        int
    :param      baudrate:    The baudrate, default 9600
    :type       baudrate:    int
    :param      data_bits:   The data bits, default 8
    :type       data_bits:   int
    :param      stop_bits:   The stop bits, default 1
    :type       stop_bits:   int
    :param      parity:      The parity, default None
    :type       parity:      Optional[int]
    :param      pins:        The pins as list [TX, RX]
    :type       pins:        List[Union[int, Pin], Union[int, Pin]]
    :param      ctrl_pin:    The control pin
    :type       ctrl_pin:    int
    :param      uart_id:     The ID of the used UART
    :type       uart_id:     int
    """
    def __init__(self,
                 addr: int,
                 baudrate: int = 9600,
                 data_bits: int = 8,
                 stop_bits: int = 1,
                 parity: Optional[int] = None,
                 pins: List[Union[int, Pin], Union[int, Pin]] = None,
                 ctrl_pin: int = None,
                 uart_id: int = 1):
        super().__init__(
            # set itf to Serial object, addr_list to [addr]
            Serial(uart_id=uart_id,
                   baudrate=baudrate,
                   data_bits=data_bits,
                   stop_bits=stop_bits,
                   parity=parity,
                   pins=pins,
                   ctrl_pin=ctrl_pin),
            [addr]
        )


class CommonRTUFunctions(object):
    """Common Functions for Modbus RTU servers"""

    def _calculate_crc16(self, data: bytearray) -> bytes:
        """
        Calculates the CRC16.

        :param      data:        The data
        :type       data:        bytearray

        :returns:   The crc 16.
        :rtype:     bytes
        """
        crc = 0xFFFF

        for char in data:
            crc = (crc >> 8) ^ Const.CRC16_TABLE[((crc) ^ char) & 0xFF]

        return struct.pack('<H', crc)

    def _exit_read(self, response: bytearray) -> bool:
        """
        Return on modbus read error

        :param      response:    The response
        :type       response:    bytearray

        :returns:   State of basic read response evaluation
        :rtype:     bool
        """
        if response[1] >= Const.ERROR_BIAS:
            if len(response) < Const.ERROR_RESP_LEN:
                return False
        elif (Const.READ_COILS <= response[1] <= Const.READ_INPUT_REGISTER):
            expected_len = Const.RESPONSE_HDR_LENGTH + 1 + \
                           response[2] + Const.CRC_LENGTH
            if len(response) < expected_len:
                return False
        elif len(response) < Const.FIXED_RESP_LEN:
            return False

        return True

    def _validate_resp_hdr(self,
                           response: bytearray,
                           slave_addr: int,
                           function_code: int,
                           count: bool) -> bytes:
        """
        Validate the response header.

        :param      response:       The response
        :type       response:       bytearray
        :param      slave_addr:     The slave address
        :type       slave_addr:     int
        :param      function_code:  The function code
        :type       function_code:  int
        :param      count:          The count
        :type       count:          bool

        :returns:   Modbus response content
        :rtype:     bytes
        """
        if len(response) == 0:
            raise OSError('no data received from slave')

        resp_crc = response[-Const.CRC_LENGTH:]
        expected_crc = self._calculate_crc16(
            response[0:len(response) - Const.CRC_LENGTH]
        )

        if ((resp_crc[0] is not expected_crc[0]) or
                (resp_crc[1] is not expected_crc[1])):
            raise OSError('invalid response CRC')

        if (response[0] != slave_addr):
            raise ValueError('wrong slave address')

        if (response[1] == (function_code + Const.ERROR_BIAS)):
            raise ValueError('slave returned exception code: {:d}'.
                             format(response[2]))

        hdr_length = (Const.RESPONSE_HDR_LENGTH + 1) if count else \
            Const.RESPONSE_HDR_LENGTH

        return response[hdr_length:len(response) - Const.CRC_LENGTH]

    def _form_serial_pdu(self,
                         modbus_pdu: bytes,
                         slave_addr: int) -> bytearray:
        """
        Forms the serial PDU from the Modbus PDU and slave address.

        :param      modbus_pdu:     The modbus PDU
        :type       modbus_pdu:     bytes
        :param      slave_addr:     The slave address
        :type       slave_addr:     int

        :returns:   The serial PDU with CRC
        :rtype      bytearray, optional
        """
        serial_pdu = bytearray()
        serial_pdu.append(slave_addr)
        serial_pdu.extend(modbus_pdu)

        crc = self._calculate_crc16(serial_pdu)
        serial_pdu.extend(crc)
        return serial_pdu

    def _parse_request(self,
                       req: bytearray,
                       unit_addr_list: Optional[List[int]]) \
            -> Optional[bytearray]:
        """
        Parses a request and, if valid, returns the request body.

        :param      req:                The request to parse 
        :type       req:                bytearray
        :param      unit_addr_list:     The unit address list
        :type       unit_addr_list:     Optional[list]

        :returns:   The request body (i.e. excluding CRC) if it is valid,
                    or None otherwise.
        :rtype      bytearray, optional
        """
        if len(req) < 8 or (unit_addr_list is not None and
                            req[0] not in unit_addr_list):
            return None

        req_crc = req[-Const.CRC_LENGTH:]
        req_no_crc = req[:-Const.CRC_LENGTH]
        expected_crc = self._calculate_crc16(req_no_crc)

        if (req_crc[0] != expected_crc[0]) or (req_crc[1] != expected_crc[1]):
            return None
        return req_no_crc

    def send_response(self,
                      slave_addr: int,
                      function_code: int,
                      request_register_addr: int,
                      request_register_qty: int,
                      request_data: list,
                      values: Optional[list] = None,
                      signed: bool = True) -> Optional[Awaitable]:
        """
        Send a response to a client.

        :param      slave_addr:             The slave address
        :type       slave_addr:             int
        :param      function_code:          The function code
        :type       function_code:          int
        :param      request_register_addr:  The request register address
        :type       request_register_addr:  int
        :param      request_register_qty:   The request register qty
        :type       request_register_qty:   int
        :param      request_data:           The request data
        :type       request_data:           list
        :param      values:                 The values
        :type       values:                 Optional[list]
        :param      signed:                 Indicates if signed
        :type       signed:                 bool

        :returns:   Request response - None for a synchronous server, or
                    an awaitable for an asynchronous server due to AsyncRequest
        :rtype      Awaitable, optional
        """
        modbus_pdu = functions.response(
            function_code=function_code,
            request_register_addr=request_register_addr,
            request_register_qty=request_register_qty,
            request_data=request_data,
            value_list=values,
            signed=signed
        )
        return self._send(modbus_pdu=modbus_pdu, slave_addr=slave_addr)

    def send_exception_response(self,
                                slave_addr: int,
                                function_code: int,
                                exception_code: int) -> Optional[Awaitable]:
        """
        Send an exception response to a client.

        :param      slave_addr:      The slave address
        :type       slave_addr:      int
        :param      function_code:   The function code
        :type       function_code:   int
        :param      exception_code:  The exception code
        :type       exception_code:  int

        :returns:   Request response - None for a synchronous server, or
                    an awaitable for an asynchronous server due to AsyncRequest
        :rtype      Awaitable, optional
        """
        modbus_pdu = functions.exception_response(
            function_code=function_code,
            exception_code=exception_code)
        return self._send(modbus_pdu=modbus_pdu, slave_addr=slave_addr)

    def _send(self, modbus_pdu: bytes, slave_addr: int) -> None:
        raise NotImplementedError("Must be overridden by subclasses")


class Serial(CommonRTUFunctions, CommonModbusFunctions):
    def __init__(self,
                 uart_id: int = 1,
                 baudrate: int = 9600,
                 data_bits: int = 8,
                 stop_bits: int = 1,
                 parity=None,
                 pins: List[Union[int, Pin], Union[int, Pin]] = None,
                 ctrl_pin: int = None):
        """
        Setup Serial/RTU Modbus

        :param      uart_id:     The ID of the used UART
        :type       uart_id:     int
        :param      baudrate:    The baudrate, default 9600
        :type       baudrate:    int
        :param      data_bits:   The data bits, default 8
        :type       data_bits:   int
        :param      stop_bits:   The stop bits, default 1
        :type       stop_bits:   int
        :param      parity:      The parity, default None
        :type       parity:      Optional[int]
        :param      pins:        The pins as list [TX, RX]
        :type       pins:        List[Union[int, Pin], Union[int, Pin]]
        :param      ctrl_pin:    The control pin
        :type       ctrl_pin:    int
        """
        self._uart = UART(uart_id,
                          baudrate=baudrate,
                          bits=data_bits,
                          parity=parity,
                          stop=stop_bits,
                          # timeout_chars=2,  # WiPy only
                          # pins=pins         # WiPy only
                          tx=pins[0],
                          rx=pins[1])

        if ctrl_pin is not None:
            self._ctrlPin = Pin(ctrl_pin, mode=Pin.OUT)
        else:
            self._ctrlPin = None

        char_const = data_bits + stop_bits + 2
        self._t1char = (1_000_000 * char_const) // baudrate
        if baudrate <= 19200:
            # 4010us (approx. 4ms) @ 9600 baud
            self._t35chars = (3_500_000 * char_const) // baudrate
        else:
            self._t35chars = 1750   # 1750us (approx. 1.75ms)

    def _uart_read(self) -> bytearray:
        """
        Read up to 40 bytes from UART

        :returns:   Read content
        :rtype:     bytearray
        """
        response = bytearray()

        for _ in range(1, 40):
            if self._uart.any():
                # WiPy only
                # response.extend(self._uart.readall())
                response.extend(self._uart.read())

                # variable length function codes may require multiple reads
                if self._exit_read(response):
                    break

            # wait for the maximum time between two frames
            time.sleep_us(self._t35chars)

        return response

    def _uart_read_frame(self, timeout: Optional[int] = None) -> bytearray:
        """
        Read a Modbus frame

        :param      timeout:  The timeout
        :type       timeout:  Optional[int]

        :returns:   Received message
        :rtype:     bytearray
        """
        received_bytes = bytearray()

        # set timeout to at least twice the time between two frames in case the
        # timeout was set to zero or None
        if timeout == 0 or timeout is None:
            timeout = 2 * self._t35chars  # in milliseconds

        start_us = time.ticks_us()

        # stay inside this while loop at least for the timeout time
        while (time.ticks_diff(time.ticks_us(), start_us) <= timeout):
            # check amount of available characters
            if self._uart.any():
                # remember this time in microseconds
                last_byte_ts = time.ticks_us()

                # do not stop reading and appending the result to the buffer
                # until the time between two frames elapsed
                while time.ticks_diff(time.ticks_us(),
                                      last_byte_ts) <= self._t35chars:
                    # WiPy only
                    # r = self._uart.readall()
                    r = self._uart.read()

                    # if something has been read after the first iteration of
                    # this inner while loop (during self._t35chars time)
                    if r is not None:
                        # append the new read stuff to the buffer
                        received_bytes.extend(r)

                        # update the timestamp of the last byte being read
                        last_byte_ts = time.ticks_us()

            # if something has been read before the overall timeout is reached
            if len(received_bytes) > 0:
                return received_bytes

        # return the result in case the overall timeout has been reached
        return received_bytes

    def _send(self, modbus_pdu: bytes, slave_addr: int) -> None:
        """
        Send Modbus frame via UART

        If a flow control pin has been setup, it will be controller accordingly

        :param      modbus_pdu:  The modbus Protocol Data Unit
        :type       modbus_pdu:  bytes
        :param      slave_addr:  The slave address
        :type       slave_addr:  int
        """
        serial_pdu = self._form_serial_pdu(modbus_pdu, slave_addr)
        send_start_time = 0

        if self._ctrlPin:
            self._ctrlPin(1)
            time.sleep_us(1000)     # wait until the control pin really changed
            send_start_time = time.ticks_us()

        self._uart.write(serial_pdu)

        if self._ctrlPin:
            total_frame_time_us = self._t1char * len(serial_pdu)
            while time.ticks_us() <= send_start_time + total_frame_time_us:
                machine.idle()
            self._ctrlPin(0)

    def _send_receive(self,
                      slave_addr: int,
                      modbus_pdu: bytes,
                      count: bool) -> bytes:
        """
        Send a modbus message and receive the reponse.

        :param      modbus_pdu:  The modbus Protocol Data Unit
        :type       modbus_pdu:  bytes
        :param      slave_addr:  The slave address
        :type       slave_addr:  int
        :param      count:       The count
        :type       count:       bool

        :returns:   Validated response content
        :rtype:     bytes
        """
        # flush the Rx FIFO
        self._uart.read()

        self._send(modbus_pdu=modbus_pdu, slave_addr=slave_addr)

        return self._validate_resp_hdr(response=self._uart_read(),
                                       slave_addr=slave_addr,
                                       function_code=modbus_pdu[0],
                                       count=count)

    def get_request(self,
                    unit_addr_list: Optional[List[int]] = None,
                    timeout: Optional[int] = None) -> Optional[Request]:
        """
        Check for request within the specified timeout

        :param      unit_addr_list:  The unit address list
        :type       unit_addr_list:  Optional[list]
        :param      timeout:         The timeout
        :type       timeout:         Optional[int]

        :returns:   A request object or None.
        :rtype:     Union[Request, None]
        """
        req = self._uart_read_frame(timeout=timeout)
        req_no_crc = self._parse_request(req, unit_addr_list)
        try:
            if req_no_crc is not None:
                return Request(interface=self, data=req_no_crc)
        except ModbusException as e:
            self.send_exception_response(
                slave_addr=req[0],
                function_code=e.function_code,
                exception_code=e.exception_code)
