#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Fakes of several MicroPython classes which are not available in UNIX"""

import _thread
try:
    import ulogging as logging
    from umodbus.typing import Optional, Union
except ImportError:
    import logging
    from typing import Optional, Union
from queue import Queue
import socket
import sys
import time


class MachineError(Exception):
    """Base class for exceptions in this module."""
    pass


class UART(object):
    """
    Fake Micropython UART class

    See https://docs.micropython.org/en/latest/library/machine.UART.html
    """
    # ESP32: TX=32, RX=4
    # RP2: TX=1, RX=2
    INV_RX = 4
    INV_TX = 32

    def __init__(self,
                 uart_id: int,
                 baudrate: int = 9600,
                 bits: int = 8,
                 parity: int = None,
                 stop: int = 1,
                 tx: int = 1,
                 rx: int = 2,
                 timeout: int = 0,
                 invert: int = 0) -> None:
        self._uart_id = uart_id
        if timeout == 0:
            timeout = 5.0
        self._timeout = timeout

        self.logger = self._configure_logger()

        # Standard loopback interface address (localhost)
        # Port to listen on (non-privileged ports are > 1023)
        if sys.implementation.name.lower() == 'micropython':
            # on MicroPython connect to the (potentially) running TCP server
            # see docker-compose-rtu-test.yaml at micropython-client-rtu
            self._host = '172.25.0.2'
        else:
            # on non MicroPython system connect to localhost
            self._host = '127.0.0.1'
        self._port = 65433
        self._sock = None

        self._server_lock = _thread.allocate_lock()
        self._send_queue = Queue(maxsize=10)
        self._receive_queue = Queue(maxsize=10)

        self._is_server = self.no_socket_server_exists(
            host=self._host,
            port=self._port)

        self.logger.debug('Timeout is: {}'.format(self._timeout))

        if self._is_server:
            self._sock = socket.socket()

            if sys.implementation.name.lower() == 'micropython':
                # MicroPython requires a bytearray
                # https://docs.micropython.org/en/v1.18/library/socket.html#socket.getaddrinfo
                addr_info = socket.getaddrinfo(self._host, self._port)[0][-1]
            else:
                addr_info = ((self._host, self._port))

            self._sock.bind(addr_info)
            self._sock.listen(10)
            # self._sock.settimeout(self._timeout)
            self._sock.setblocking(False)

            self.logger.debug('Bound to {} on {}'.
                              format(self._host, self._port))

            # start the socket server thread as soon as init is done
            self.serving = True
        else:
            self._sock = socket.socket()
            self._sock.settimeout(self._timeout)
            # self._sock.setblocking(False)

            if sys.implementation.name.lower() == 'micropython':
                # MicroPython requires a bytearray
                # https://docs.micropython.org/en/v1.18/library/socket.html#socket.socket.connect
                addr_info = socket.getaddrinfo(self._host, self._port)[0][-1]
            else:
                addr_info = ((self._host, self._port))

            self._sock.connect(addr_info)
            self.logger.debug('Connecting to {} on {}'.
                              format(self._host, self._port))

        self.logger.debug('Will act as {}'.
                          format('server' if self._is_server else 'client'))

    def _configure_logger(self) -> logging.Logger:
        """
        Create and configure a logger

        :returns:   Configured logger
        :rtype:     logging.Logger
        """
        if sys.implementation.name.lower() == 'micropython':
            logging.basicConfig(level=logging.INFO)
        else:
            custom_format = '[%(asctime)s] [%(levelname)-8s] [%(filename)-15s'\
                            ' @ %(funcName)-15s:%(lineno)4s] %(message)s'
            logging.basicConfig(level=logging.INFO,
                                format=custom_format,
                                stream=sys.stdout)

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        return logger

    def no_socket_server_exists(self,
                                host: str,
                                port: int,
                                timeout: Optional[float] = 1.0) -> bool:
        """
        Determines if no socket server exists.

        :param      host:     The host IP
        :type       host:     str
        :param      port:     The port
        :type       port:     int
        :param      timeout:  The timeout
        :type       timeout:  float

        :returns:   True if no socket server exists, False otherwise.
        :rtype:     bool
        """
        become_server = True

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        try:
            if sys.implementation.name.lower() == 'micropython':
                # MicroPython requires a bytearray
                # https://docs.micropython.org/en/v1.18/library/socket.html#socket.socket.connect
                addr_info = socket.getaddrinfo(host, port)[0][-1]
            else:
                addr_info = ((host, port))
            sock.connect(addr_info)
        except Exception:
            self.logger.debug('Exception during potential server connect')
            self.logger.debug('Failed to connect to {} on {}'.
                              format(host, port))
            sock.close()
            # assume no server is available
            # this device shall thereby become a server itself
            return become_server

        self.logger.debug('Connection to server successful')

        # send test message to server
        sock.send(b'Ping. Hello UART server?')  # not the best message
        self.logger.debug('Sent ping to potential server')

        # wait for specified timeout for a response from the server
        try:
            received_data = sock.recv(127)
            if received_data:
                self.logger.info('Received as response to ping: {}'.
                                 format(received_data))
                if received_data == b'pong':
                    # a potential server shall respond with b'pong'.
                    # The return value shall thereby by "False", as the
                    # check for no socket server existance failed
                    become_server = False
        except OSError as e:
            # 11 = timeout expired (MicroPython)
            # 35 = Resource temporarily unavailable (Python OS X)
            # "timed out" (Python Windows)
            if e.args[0] in [11, 35, 'timed out']:
                self.logger.debug('Timeout waiting for server response')
            else:
                raise e

        sock.close()

        return become_server

    @property
    def is_server(self) -> bool:
        """
        Determines if this object acts as server aka UART host.

        :returns:   True if server, False otherwise.
        :rtype:     bool
        """
        return self._is_server

    @property
    def serving(self) -> bool:
        """
        Get the server status.

        :returns:   Flag whether socket server is running or not.
        :rtype:     bool
        """
        return self._server_lock.locked()

    @serving.setter
    def serving(self, value: bool) -> None:
        """
        Start or stop running the socket server.

        :param      value:  The value
        :type       value:  bool
        """
        if value and (not self._server_lock.locked()):
            # start socket server if not already running
            self._server_lock.acquire()

            # parameters of the _serve function
            params = (
                self._sock,
                self._send_queue,
                self._receive_queue,
                self._server_lock,
                self.logger
            )
            _thread.start_new_thread(self._serve, params)
            self.logger.info('Socket {} started'.
                             format('server' if self._is_server else 'client'))
        elif (value is False) and self._server_lock.locked():
            # stop server if not already stopped
            self._server_lock.release()
            self.logger.info('Socket {} lock released'.
                             format('server' if self._is_server else 'client'))

    def _serve(self,
               sock: socket,
               send_queue: Queue,
               receive_queue: Queue,
               lock: int,
               logger: logging.Logger) -> None:
        """
        Internal socket server function

        :param      sock:           The socket
        :type       sock:           socket
        :param      send_queue:     The send queue
        :type       send_queue:     Queue
        :param      receive_queue:  The receive queue
        :type       receive_queue:  Queue
        :param      lock:           The lock flag
        :type       lock:           int
        :param      logger:         The logger
        :type       logger:         logging.Logger
        """
        if sock is None:
            raise Exception('Server not bound')
        else:
            logger.info('Acting as server')

        _client_sock = None

        while lock.locked():
            new_client_sock = None

            try:
                # either a connection is made from a client or
                # an OSError is thrown after the configured timeout
                new_client_sock, addr = sock.accept()
            except OSError as e:
                # 11 = timeout expired (MicroPython)
                # 35 = Resource temporarily unavailable (Python OS X)
                # "timed out" (Python Windows)
                if e.args[0] not in [11, 35, 'timed out']:
                    logger.warning('OSError {}: {}'.
                                   format(e, e.args[0]))

            if new_client_sock is not None:
                logger.debug('Connection from {}'.format(addr))
                if _client_sock is not None:
                    logger.debug('Closed connection to last client')
                    _client_sock.close()

                _client_sock = new_client_sock
                _client_sock.settimeout(0.5)

            if _client_sock is not None:
                # get client message
                try:
                    received_data = _client_sock.recv(127)

                    # log data and send response
                    if received_data:
                        logger.info('Received from client: {}'.
                                    format(received_data))

                        if received_data == b'Ping. Hello UART server?':
                            _client_sock.send(b'pong')
                            logger.info('Responded with "pong"')
                        else:
                            receive_queue.put_nowait(received_data)

                            # grant host enough time to process received
                            # data, prepare a response for the client and put
                            # it into the send_queue
                            # Sleep time shall be less than client timeout
                            # specified during UART init
                            # Approx. process time is below 100ms
                            time.sleep(0.1)
                except Exception as e:
                    logger.debug('Error during connection: {}'.format(e))
                    _client_sock.close()
                    _client_sock = None

                if send_queue.qsize():
                    send_data = send_queue.get_nowait()

                    logger.info('Responding to client: {}'.
                                format(send_data))
                    _client_sock.send(send_data)

    def deinit(self) -> None:
        """Turn off the UART bus"""
        raise MachineError('Not yet implemented')

    def any(self) -> int:
        """
        Return number of characters available.

        Mock does not return the actual number of characters but the elements
        in the receive queue. Which is usually "0" or "1"

        :returns:   Number of characters available
        :rtype:     int
        """
        available_data_amount = 0

        if self._is_server:
            available_data_amount = self._receive_queue.qsize()
        else:
            # patch available data, as reading the socket buffer would drain it
            available_data_amount = 1

        return available_data_amount

    def read(self, nbytes: Optional[int] = None) -> Union[None, bytes]:
        """
        Read characters

        :param      nbytes:  The amount of bytes to read
        :type       nbytes:  int

        :returns:   Bytes read, None on timeout
        :rtype:     Union[None, bytes]
        """
        data = None

        if self._is_server:
            if self._receive_queue.qsize():
                data = self._receive_queue.get_nowait()
        else:
            try:
                data = self._sock.recv(127)
            except OSError as e:
                self.logger.warning('OSError {}: {}'.format(e, e.args[0]))

        return data

    def readinto(self,
                 buf: bytes,
                 nbytes: Optional[int] = None) -> Union[None, bytes]:
        """
        Read bytes into the buffer.

        If nbytes is specified then read at most that many bytes. Otherwise,
        read at most len(buf) bytes

        :param      buf:     The buffer
        :type       buf:     bytes
        :param      nbytes:  The nbytes
        :type       nbytes:  Optional[int]

        :returns:   Number of bytes read and stored in buffer, None on timeout
        :rtype:     Union[None, bytes]
        """
        raise MachineError('Not yet implemented')

    def readline(self) -> Union[None, str]:
        """
        Read a line, ending in a newline character

        :returns:   The line read, None on timeout.
        :rtype:     Union[None, str]
        """
        raise MachineError('Not yet implemented')

    def write(self, buf: bytes) -> Union[None, int]:
        """
        Write the buffer of bytes to the bus

        :param      buf:  The buffer
        :type       buf:  bytes

        :returns:   Number of bytes written, None on timeout
        :rtype:     Union[None, int]
        """
        if self._is_server:
            self._send_queue.put_nowait(buf)
        else:
            self._sock.send(buf)

        return len(buf)

    def sendbreak(self) -> None:
        """Send a break condition on the bus"""
        raise MachineError('Not yet implemented')

    '''
    # flush introduced in MicroPython v1.20.0
    # use manual timing calculation for testing
    def flush(self) -> None:
        """
        Waits until all data has been sent

        In case of a timeout, an exception is raised

        Only available with newer versions than 1.19
        """
        raise MachineError('Not yet implemented')
    '''

    def txdone(self) -> bool:
        """
        Tells whether all data has been sent or no data transfer is happening

        :returns:   If data transmission is ngoing return False, True otherwise
        :rtype:     bool
        """
        raise MachineError('Not yet implemented')


class Pin(object):
    """
    Fake Micropython Pin class

    See https://docs.micropython.org/en/latest/library/machine.Pin.html
    """
    IN = 1
    OUT = 2

    def __init__(self, pin: int, mode: int):
        self._pin = pin
        self._mode = mode
        self._value = False

    def value(self, val: Optional[Union[int, bool]] = None) -> Optional[bool]:
        """
        Set or get the value of the pin

        :param      val:  The value
        :type       val:  Optional[Union[int, bool]]

        :returns:   State of the pin if no value specifed, None otherwise
        :rtype:     Optional[bool]
        """
        if val is not None and self._mode == Pin.OUT:
            # set pin state
            self._value = bool(val)
        else:
            # get pin state
            return self._value

    def on(self) -> None:
        """Set pin to "1" output level"""
        if self._mode == Pin.OUT:
            self.value(val=True)

    def off(self) -> None:
        """Set pin to "0" output level"""
        if self._mode == Pin.OUT:
            self.value(val=False)
