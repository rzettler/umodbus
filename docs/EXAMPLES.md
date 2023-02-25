# Examples

Usage examples of this `micropython-modbus` library

---------------

## RTU

```{note}
Check the port specific
[MicroPython UART documentation](https://docs.micropython.org/en/latest/library/machine.UART.html)
for further details.

A Raspberry Pi Pico e.g. requires the UART pins as a tuple of `Pin`, like
`rtu_pins = (Pin(4), Pin(5))` and the corresponding `uart_id` for those pins,
whereas ESP32 boards can use almost any pin for UART communication as shown in
the following examples and shall be given as `rtu_pins = (25, 26)`. If
necessary, the `uart_id` parameter may has to be adapted to the pins used.
```

### Client/Slave

With this example the device is acting as client (slave) and providing data via
RTU (serial/UART) to a requesting host device.

```python
from umodbus.serial import ModbusRTU

# RTU Client/Slave setup

# the following definition is for an ESP32
rtu_pins = (25, 26)         # (TX, RX)
uart_id = 1

# the following definition is for a RP2
# rtu_pins = (Pin(0), Pin(1))     # (TX, RX)
# uart_id = 0
#
# rtu_pins = (Pin(4), Pin(5))     # (TX, RX)
# uart_id = 1

# the following definition is for a pyboard
# rtu_pins = (Pin(PB6), Pin(PB7))   # (TX, RX)
# uart_id = 1

slave_addr = 10             # address on bus as client

client = ModbusRTU(
    addr=slave_addr,        # address on bus
    pins=rtu_pins,          # given as tuple (TX, RX)
    # baudrate=9600,        # optional, default 9600
    # data_bits=8,          # optional, default 8
    # stop_bits=1,          # optional, default 1
    # parity=None,          # optional, default None
    # ctrl_pin=12,          # optional, control DE/RE
    uart_id=uart_id         # optional, default 1, see port specific documentation
)

register_definitions = {
    "COILS": {
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

# use the defined values of each register type provided by register_definitions
client.setup_registers(registers=register_definitions)

while True:
    try:
        result = client.process()
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping RTU client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))
```

### Host/Master

With this example the device is acting as host (master) and requesting on or
setting data at a RTU (serial/UART) client/slave.

```python
from umodbus.serial import Serial as ModbusRTUMaster

# RTU Host/Master setup

# the following definition is for an ESP32
rtu_pins = (25, 26)         # (TX, RX)
uart_id = 1

# the following definition is for a RP2
# rtu_pins = (Pin(0), Pin(1))     # (TX, RX)
# uart_id = 0
#
# rtu_pins = (Pin(4), Pin(5))     # (TX, RX)
# uart_id = 1

# the following definition is for a pyboard
# rtu_pins = (Pin(PB6), Pin(PB7))   # (TX, RX)
# uart_id = 1

host = ModbusRTUMaster(
    pins=rtu_pins,          # given as tuple (TX, RX)
    # baudrate=9600,        # optional, default 9600
    # data_bits=8,          # optional, default 8
    # stop_bits=1,          # optional, default 1
    # parity=None,          # optional, default None
    # ctrl_pin=12,          # optional, control DE/RE
    uart_id=uart_id         # optional, default 1, see port specific documentation
)

coil_status = host.read_coils(slave_addr=10, starting_addr=123, coil_qty=1)
print('Status of coil 123: {}'.format(coil_status))
```

## TCP

### Client/Slave

With this example the device is acting as client (slave) and providing data via
TCP (socket) to a requesting host device.

```python
import network
from umodbus.tcp import ModbusTCP

# network connections shall be made here, check the MicroPython port specific
# documentation for connecting to or creating a network

# TCP Client/Slave setup
# set IP address of this MicroPython device explicitly
# local_ip = '192.168.4.1'  # IP address
# or get it from the system after a connection to the network has been made
# it is not the task of this lib to provide a detailed explanation for this
station = network.WLAN(network.STA_IF)
local_ip = station.ifconfig()[0]
tcp_port = 502      # port to listen for requests/providing data

client = ModbusTCP()

# check whether client has been bound to an IP and a port
if not client.get_bound_status():
    client.bind(local_ip=local_ip, local_port=tcp_port)

register_definitions = {
    "COILS": {
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

# use the defined values of each register type provided by register_definitions
client.setup_registers(registers=register_definitions)

while True:
    try:
        result = client.process()
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping TCP client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))
```

### Host/Master

With this example the device is acting as host (master) and requesting on or
setting data at a TCP (socket) client/slave.

```python
from umodbus.tcp import TCP as ModbusTCPMaster

# valid network connections shall be made here

# RTU Host/Master setup
slave_tcp_port = 502            # port to send request on
slave_ip = '192.168.178.69'     # IP address of client, to be adjusted

host = ModbusTCPMaster(
    slave_ip=slave_ip,
    slave_port=slave_tcp_port,
    # timeout=5.0               # optional, timeout in seconds, default 5.0
)

coil_status = host.read_coils(slave_addr=10, starting_addr=123, coil_qty=1)
print('Status of coil 123: {}'.format(coil_status))
```

## Callbacks

Callbacks can be registered to be executed *after* setting a register with
`on_set_cb` or to be executed *before* getting a register with `on_get_cb`.

```{note}
Getter callbacks can be registered for all registers with the `on_get_cb`
parameter whereas the `on_set_cb` parameter is only available for coils and
holding registers as only those can be set by a external host.
```

```{eval-rst}
.. warning::
    Keep the get callback actions as short as possible to avoid potential
    request timeouts due to a to long processing time.
```

```python
def my_coil_set_cb(reg_type, address, val):
    print('Custom callback, called on setting {} at {} to: {}'.
          format(reg_type, address, val))


def my_coil_get_cb(reg_type, address, val):
    print('Custom callback, called on getting {} at {}, currently: {}'.
          format(reg_type, address, val))


# define some registers, for simplicity only a single coil is used
register_definitions = {
    "COILS": {
        "EXAMPLE_COIL": {
            "register": 123,
            "len": 1,
            "val": 1,
            "on_get_cb": my_coil_get_cb,
            "on_set_cb": my_coil_set_cb
        }
    }
}

# use the defined values of each register type provided by register_definitions
client.setup_registers(registers=register_definitions)

# callbacks can also be defined after a register setup has been performed
client.add_coil(
    address=123,
    value=bool(1),
    on_set_cb=my_coil_set_cb,
    on_get_cb=my_coil_get_cb
)
```
