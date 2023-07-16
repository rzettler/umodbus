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
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from ..sys_imports import time, Pin, Callable, Coroutine
from ..sys_imports import List, Tuple, Optional, Union, Any

# custom packages
from .common import CommonAsyncModbusFunctions, AsyncRequest
from ..common import ModbusException
from .modbus import AsyncModbus
from ..serial import CommonRTUFunctions, RTUServer

US_TO_S = 1 / 1_000_000


class AsyncModbusRTU(AsyncModbus):
    """
    Asynchronous Modbus RTU server

    @see ModbusRTU
    """
    def __init__(self,
                 addr: int,
                 baudrate: int = 9600,
                 data_bits: int = 8,
                 stop_bits: int = 1,
                 parity: Optional[int] = None,
                 pins: Tuple[Union[int, Pin], Union[int, Pin]] = None,
                 ctrl_pin: int = None,
                 uart_id: int = 1):
        super().__init__(
            # set itf to AsyncRTUServer object, addr_list to [addr]
            AsyncRTUServer(uart_id=uart_id,
                           baudrate=baudrate,
                           data_bits=data_bits,
                           stop_bits=stop_bits,
                           parity=parity,
                           pins=pins,
                           ctrl_pin=ctrl_pin),
            [addr]
        )

    async def bind(self) -> None:
        """@see AsyncRTUServer.bind"""

        await self._itf.bind()

    async def serve_forever(self) -> None:
        """@see AsyncRTUServer.serve_forever"""

        await self._itf.serve_forever()

    def server_close(self) -> None:
        """@see AsyncRTUServer.server_close"""

        self._itf.server_close()


class AsyncRTUServer(RTUServer):
    """Asynchronous Modbus Serial host"""

    def __init__(self,
                 uart_id: int = 1,
                 baudrate: int = 9600,
                 data_bits: int = 8,
                 stop_bits: int = 1,
                 parity=None,
                 pins: Tuple[Union[int, Pin], Union[int, Pin]] = None,
                 ctrl_pin: int = None):
        """
        Setup asynchronous Serial/RTU Modbus

        @see RTUServer
        """
        super().__init__(uart_id=uart_id,
                         baudrate=baudrate,
                         data_bits=data_bits,
                         stop_bits=stop_bits,
                         parity=parity,
                         pins=pins,
                         ctrl_pin=ctrl_pin)

        self._task = None
        self.event = asyncio.Event()
        self.req_handler: Callable[[Optional[AsyncRequest]],
                                   Coroutine[Any, Any, bool]] = None
        self._uart_reader = asyncio.StreamReader(self._uart)
        self._uart_writer = asyncio.StreamWriter(self._uart, {})

    async def bind(self) -> None:
        """
        Starts serving the asynchronous server on the specified host and port
        specified in the constructor.
        """

        self._task = asyncio.create_task(self._uart_bind())

    async def _uart_bind(self) -> None:
        """Starts processing requests continuously. Must be run as a task."""

        if self.req_handler is None:
            raise ValueError("No req_handler detected. "
                             "This may be because this class object was "
                             "instantiated manually, and not as part of "
                             "a Modbus server.")
        while not self.event.is_set():
            # form request and pass to process in infinite loop
            await self.req_handler()

    async def serve_forever(self) -> None:
        """Waits for the server to close."""

        if self._task is None:
            raise ValueError("Error: must call bind() first")
        await self._task

    def server_close(self) -> None:
        """Stops a running server, i.e. stops reading from UART."""

        self.event.set()

    async def _uart_read_frame(self,
                               timeout: Optional[int] = None) -> bytearray:
        """@see Serial._uart_read_frame"""

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
                    data = self._uart.read()

                    # if something has been read after the first iteration of
                    # this inner while loop (during self._t35chars time)
                    if data is not None:
                        # append the new read stuff to the buffer
                        received_bytes.extend(data)

                        # update the timestamp of the last byte being read
                        last_byte_ts = time.ticks_us()

            # if something has been read before the overall timeout is reached
            if len(received_bytes) > 0:
                return received_bytes

        # return the result in case the overall timeout has been reached
        return received_bytes

        # set timeout to at least twice the time between two
        # frames in case the timeout was set to zero or None
        # if not timeout:
        #    timeout = 2 * self._t35chars  # in milliseconds
        #
        # received_bytes = bytearray()
        # total_timeout = timeout * US_TO_S
        # frame_timeout = self._t35chars * US_TO_S
        #
        # try:
        #    wait until overall timeout to read at least one byte
        #    current_timeout = total_timeout
        #    while True:
        #        read_task = self._uart_reader.read()
        #        print("2.3.1.1 waiting for data from UART")
        #        data = await asyncio.wait_for(read_task, current_timeout)
        #        print("2.3.1.2 received data from UART")
        #        received_bytes.extend(data)
        #
        #        if data received, switch to waiting until inter-frame
        #        timeout is exceeded, to delineate two separate frames
        #        current_timeout = frame_timeout
        # except asyncio.TimeoutError:
        #    print("2.3.1.3 timeout occurred when waiting for data from UART")
        #    pass  # stop when no data left to read before timeout
        # print("2.3.1.4 data from UART is:", received_bytes)
        # return received_bytes

    async def send_response(self,
                            slave_addr: int,
                            function_code: int,
                            request_register_addr: int,
                            request_register_qty: int,
                            request_data: list,
                            values: Optional[list] = None,
                            signed: bool = True,
                            request: Optional[AsyncRequest] = None) -> None:
        """
        Asynchronous equivalent to Serial.send_response
        @see Serial.send_response for common (leading) parameters

        :param      request:     Ignored; kept for compatibility
                                 with AsyncRequest
        :type       request:     AsyncRequest, optional
        """

        task = super().send_response(slave_addr=slave_addr,
                                     function_code=function_code,
                                     request_register_addr=request_register_addr,  # noqa: E501
                                     request_register_qty=request_register_qty,
                                     request_data=request_data,
                                     values=values,
                                     signed=signed)
        if task is not None:
            await task

    async def send_exception_response(self,
                                      slave_addr: int,
                                      function_code: int,
                                      exception_code: int,
                                      request: Optional[AsyncRequest] = None) \
            -> None:
        """
        Asynchronous equivalent to Serial.send_exception_response
        @see Serial.send_exception_response for common (leading) parameters

        :param      request:     Ignored; kept for compatibility
                                 with AsyncRequest
        :type       request:     AsyncRequest, optional
        """

        task = super().send_exception_response(slave_addr=slave_addr,
                                               function_code=function_code,
                                               exception_code=exception_code)
        if task is not None:
            await task

    async def get_request(self,
                          unit_addr_list: Optional[List[int]] = None,
                          timeout: Optional[int] = None) -> \
            Optional[AsyncRequest]:
        """@see Serial.get_request"""

        req = await self._uart_read_frame(timeout=timeout)
        req_no_crc = self._parse_request(req=req,
                                         unit_addr_list=unit_addr_list)
        try:
            if req_no_crc is not None:
                print("2.3.4 creating AsyncRequest")
                return AsyncRequest(interface=self, data=req_no_crc)
        except ModbusException as e:
            print("2.3.5 exception occurred when creating AsyncRequest:", e)
            await self.send_exception_response(slave_addr=req[0],
                                               function_code=e.function_code,
                                               exception_code=e.exception_code)

    async def _send(self,
                    modbus_pdu: bytes,
                    slave_addr: int) -> None:
        """@see CommonRTUFunctions._send"""

        await _async_send(device=self,
                          modbus_pdu=modbus_pdu,
                          slave_addr=slave_addr)

    def set_params(self,
                   addr_list: Optional[List[int]],
                   req_handler: Callable[[Optional[AsyncRequest]],
                                         Coroutine[Any, Any, bool]]) -> None:
        """
        Used to set parameters such as the unit address list
        and the processing handler.

        :param      addr_list:      The unit address list, currently ignored
        :type       addr_list:      List[int], optional
        :param      req_handler:    A callback that is responsible for parsing
                                    individual requests from a Modbus client
        :type       req_handler:    (Optional[AsyncRequest]) ->
                                        (() -> bool, async)
        """

        self.req_handler = req_handler


class AsyncSerial(CommonRTUFunctions, CommonAsyncModbusFunctions):
    """Asynchronous Modbus Serial client"""

    def __init__(self,
                 uart_id: int = 1,
                 baudrate: int = 9600,
                 data_bits: int = 8,
                 stop_bits: int = 1,
                 parity=None,
                 pins: Tuple[Union[int, Pin], Union[int, Pin]] = None,
                 ctrl_pin: int = None):
        """
        Setup asynchronous Serial/RTU Modbus

        @see Serial
        """
        super().__init__(uart_id=uart_id,
                         baudrate=baudrate,
                         data_bits=data_bits,
                         stop_bits=stop_bits,
                         parity=parity,
                         pins=pins,
                         ctrl_pin=ctrl_pin)

        self._uart_reader = asyncio.StreamReader(self._uart)
        self._uart_writer = asyncio.StreamWriter(self._uart, {})

    async def _uart_read(self) -> bytearray:
        """@see Serial._uart_read"""

        response = bytearray()
        wait_period = self._t35chars * US_TO_S

        for _ in range(1, 40):
            # WiPy only
            # response.extend(await self._uart_reader.readall())
            response.extend(await self._uart_reader.read())

            # variable length function codes may require multiple reads
            if self._exit_read(response):
                break

            # wait for the maximum time between two frames
            await asyncio.sleep(wait_period)

        return response

    async def _uart_read_frame(self,
                               timeout: Optional[int] = None) -> bytearray:
        """@see Serial._uart_read_frame"""

        # set timeout to at least twice the time between two
        # frames in case the timeout was set to zero or None
        if not timeout:
            timeout = 2 * self._t35chars  # in milliseconds

        received_bytes = bytearray()
        total_timeout = timeout * US_TO_S
        frame_timeout = self._t35chars * US_TO_S

        try:
            # wait until overall timeout to read at least one byte
            current_timeout = total_timeout
            while True:
                read_task = self._uart_reader.read()
                data = await asyncio.wait_for(read_task, current_timeout)
                received_bytes.extend(data)

                # if data received, switch to waiting until inter-frame
                # timeout is exceeded, to delineate two separate frames
                current_timeout = frame_timeout
        except asyncio.TimeoutError:
            pass  # stop when no data left to read before timeout
        return received_bytes

    async def _send(self,
                    modbus_pdu: bytes,
                    slave_addr: int) -> None:
        """@see Serial._send"""

        await _async_send(device=self,
                          modbus_pdu=modbus_pdu,
                          slave_addr=slave_addr)

    async def _send_receive(self,
                            slave_addr: int,
                            modbus_pdu: bytes,
                            count: bool) -> bytes:
        """@see Serial._send_receive"""

        # flush the Rx FIFO
        await self._uart_reader.read()
        await self._send(modbus_pdu=modbus_pdu, slave_addr=slave_addr)

        response = await self._uart_read()
        return self._validate_resp_hdr(response=response,
                                       slave_addr=slave_addr,
                                       function_code=modbus_pdu[0],
                                       count=count)

    async def send_response(self,
                            slave_addr: int,
                            function_code: int,
                            request_register_addr: int,
                            request_register_qty: int,
                            request_data: list,
                            values: Optional[list] = None,
                            signed: bool = True,
                            request: Optional[AsyncRequest] = None) -> None:
        """
        Asynchronous equivalent to Serial.send_response
        @see Serial.send_response for common (leading) parameters

        :param      request:     Ignored; kept for compatibility
                                 with AsyncRequest
        :type       request:     AsyncRequest, optional
        """

        task = super().send_response(slave_addr=slave_addr,
                                     function_code=function_code,
                                     request_register_addr=request_register_addr,  # noqa: E501
                                     request_register_qty=request_register_qty,
                                     request_data=request_data,
                                     values=values,
                                     signed=signed)
        if task is not None:
            await task

    async def send_exception_response(self,
                                      slave_addr: int,
                                      function_code: int,
                                      exception_code: int,
                                      request: Optional[AsyncRequest] = None) \
            -> None:
        """
        Asynchronous equivalent to Serial.send_exception_response
        @see Serial.send_exception_response for common (leading) parameters

        :param      request:     Ignored; kept for compatibility
                                 with AsyncRequest
        :type       request:     AsyncRequest, optional
        """

        task = super().send_exception_response(slave_addr=slave_addr,
                                               function_code=function_code,
                                               exception_code=exception_code)
        if task is not None:
            await task

    async def get_request(self,
                          unit_addr_list: Optional[List[int]] = None,
                          timeout: Optional[int] = None) -> \
            Optional[AsyncRequest]:
        """@see Serial.get_request"""

        req = await self._uart_read_frame(timeout=timeout)
        req_no_crc = self._parse_request(req=req,
                                         unit_addr_list=unit_addr_list)
        try:
            if req_no_crc is not None:
                return AsyncRequest(interface=self, data=req_no_crc)
        except ModbusException as e:
            await self.send_exception_response(slave_addr=req[0],
                                               function_code=e.function_code,
                                               exception_code=e.exception_code)


async def _async_send(device: Union[AsyncRTUServer, AsyncSerial],
                      modbus_pdu: bytes,
                      slave_addr: int) -> None:
    """
    Send modbus frame via UART asynchronously

    Note: This is not part of a class because the _send()
    function exists in CommonRTUFunctions, which RTUServer
    extends. Putting this in a CommonAsyncRTUFunctions class
    would result in a rather strange MRO/inheritance chain,
    so the _send functions in the client and server just
    delegate to this function.

    :param      device:     The self object calling this function
    :type       device:     Union[AsyncRTUServer, AsyncSerial]

    @see CommonRTUFunctions._send
    """

    serial_pdu = device._form_serial_pdu(modbus_pdu, slave_addr)
    send_start_time = 0

    if device._ctrlPin:
        device._ctrlPin(1)
        # wait 1 ms to ensure control pin has changed
        await asyncio.sleep(1 / 1000)
        send_start_time = time.ticks_us()

    device._uart_writer.write(serial_pdu)
    await device._uart_writer.drain()

    if device._ctrlPin:
        total_frame_time_us = device._t1char * len(serial_pdu)
        target_time = send_start_time + total_frame_time_us
        time_difference = target_time - time.ticks_us()
        # idle until data sent
        await asyncio.sleep(time_difference * US_TO_S)
        device._ctrlPin(0)
