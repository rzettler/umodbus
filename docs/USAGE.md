# Usage

Overview to use this `micropython-modbus` library

---------------

```{note}
The onwards described steps assume a successful setup as described in the
[setup chapter](SETUP.md)

Further examples are available in the [examples chapter](EXAMPLES.md)
```

## Register configuration

The available registers can be defined by a JSON file, placed inside the
`/pyboard/registers` folder or any other location on the board and loaded in
`main.py` or by defining a dictionary.

As an [example the registers][ref-registers-MyEVSE] of a
[brainelectronics MyEVSE][ref-myevse-be], [MyEVSE on Tindie][ref-myevse-tindie]
board and others are provided with this repo.

### Structure

If only an interaction with a single register is intended no dictionary needs
to be defined of course. The onwards explanations assume a bigger setup of
registers on the same target/client/slave device.

The JSON file/dictionary shall follow the following pattern/structure

```python
{
    "COILS": {          # this key shall contain all coils
        "COIL_NAME": {  # custom name of a coil
            "register": 42,     # register address of the coil
            "len": 1,           # amount of registers to request aka quantity
            "val": 0,           # used to set a register
            # the onwards mentioned keys are optional
            "description": "Optional description of the coil",
            "range": "[0, 1]",  # may provide a range of the value, only for documentation purpose
            "unit": "BOOL",     # may provide a unit of the value, only for documentation purpose
            "on_set_cb": my_function,   # callback function executed on the client after a new value has been set
            "on_get_cb": some_function  # callback function executed on the client after a value has been requested
        }
    },
    "HREGS": {          # this key shall contain all holding registers
        "HREG_NAME": {  # custom name of a holding register
            "register": 93,     # register address of the holding register
            "len": 1,           # amount of registers to request aka quantity
            "val": 19,          # used to set a register
            "description": "Optional description of the holding register",
            "range": "[0, 65535]",
            "unit": "Hz",
            "on_set_cb": my_function,   # callback function executed on the client after a new value has been set
            "on_get_cb": some_function  # callback function executed on the client after a value has been requested
        },
    },
    "ISTS": {           # this key shall contain all input status registers
        "ISTS_NAME": {  # custom name of a input status register
            "register": 67,     # register address of the input status register
            "len": 1,           # amount of registers to request aka quantity
            "val": 0,           # used to set a register, not possible for ISTS
            "description": "Optional description of the input status register",
            "range": "[0, 1]",
            "unit": "activated",
            "on_get_cb": some_function  # callback function executed on the client after a value has been requested
        }
    },
    "IREGS": {          # this key shall contain all input registers
        "IREG_NAME": {  # custom name of an input register
            "register": 10,     # register address of the input register
            "len": 1,           # amount of registers to request aka quantity
            "val": 60001,       # used to set a register, not possible for IREGS
            "description": "Optional description of the static input register",
            "range": "[0, 65535]",
            "unit": "millivolt",
            "on_get_cb": some_function  # callback function executed on the client after a value has been requested
        }
    }
}
```

If not all register types are used they can be of course removed from the
JSON file/dictionary. The smallest possible definition for reading a coil
would look like

```python
{
    "COILS": {          # this key shall contain all coils
        "COIL_NAME": {  # custom name of a coil
            "register": 42,     # register address of the coil
            "len": 1            # amount of registers to request aka quantity
        }
    }
}
```

In order to act as client/slave device the same structure can be used. If no
`val` element is found in the structure the default values are

| Type  | Function Code | Default value |
| ----- | ------------- | ------------- |
| COILS | 0x01 | False (0x0) |
| ISTS  | 0x02 | False (0x0) |
| HREGS | 0x03 | 0 |
| IREGS | 0x04 | 0 |

The value of multiple registers can be set like this

```python
{
    "HREGS": {          # this key shall contain all holding registers
        "HREG_NAME": {  # custom name of a holding register
            "register": 93,     # register address of the holding register
            "len": 3,           # amount of registers to request aka quantity
            "val": [29, 38, 0]  # used to set a register
        }
    }
}
```

### Detailed key explanation

The onwards described key explanations are valid for COIL, HREG, IST and IREG

#### Register

The key `register` defines the register to request or manipulate.

According to the Modbus specification the register address has to be in the
range of 0x0000 to 0xFFFF (65535) to be valid.

#### Length

The key `len` defines the amout of registers to be requested starting from/with
the defined `register` address.

According to the Modbus specification the length or amount depends on the type
of the register as summarized in the table below.

| Type  | Function Code | Valid range |
| ----- | ------------- | ----------- |
| COILS | 0x01 | 0x1 to 0x7D0 (2000)  |
| ISTS  | 0x02 | 0x1 to 0x7D0 (2000)  |
| HREGS | 0x03 | 0x1 to 0x7D (125)    |
| IREGS | 0x04 | 0x1 to 0x7D (125)    |

In order to read 5 coils starting at 124 use the following dictionary aka
config

```python
{
    "COILS": {          # this key shall contain all coils
        "COIL_NAME": {  # custom name of a coil
            "register": 124,    # register address of the coil
            "len": 5            # amount of registers to request aka quantity
        }
    }
}
```

The output will be a list of 5 elements like `[True, False, False, True, True]`
depending on the actual device coil states of course.

#### Value

The key `val` defines the value of registers to be set on the target/client
device.

According to the Modbus specification the value (range) depends on the type
of the register as summarized in the table below.

| Type | Function Code | Valid value | Comment |
| ---- | ------------- | ----------- | ------- |
| COILS | 0x05 | 0x0000 or 0xFF00 | This package maps `0` or `False` to `0x0000` and `1` or `True` to `0xFF00` |
| HREGS | 0x06 | 0x0000 to 0xFFFF (65535) |  |

#### Optional description

The optional key `description` can be used to provide an additional
description of the register. This might be helpful if the register name is not
meaninful enough or for any other reason of course.

#### Optional range

The optional key `range` can be used to indicate the possible value range of
this specific target. For example a holding register for setting a PWM output
might only support a range of 0 to 100. This might be especially helpful with
the optional [`unit`](#optional-unit) key.

##### Optional unit

The optional key `unit` can be used to provide further details about the unit
of the register. In case of the PWM output register example of the
[optional range key](#optional-range) the recommended value for this key could
be `percent`.

##### Optional callbacks

The optional keys `on_set_cb` and `on_get_cb` can be used to register a
callback function on client side which is executed **after** a new value has
been set or **before** the response of a requested register value has been
sent.

```{note}
Getter callbacks can be registered for all registers with the `on_get_cb`
parameter whereas the `on_set_cb` parameter is only available for coils and
holding registers as only those can be set by a external host.
```

The callback function shall have the following three parameters:

| Parameter  | Type | Description |
| ---------- | ------ | -------------------|
| `reg_type` | string | Type of register. `COILS`, `HREGS`, `ISTS`, `IREGS` |
| `address`  | int | Type of register. `COILS`, `HREGS`, `ISTS`, `IREGS` |
| `val`      | Union[bool, int, Tuple[bool], Tuple[int], List[bool], List[int]] | Current value of register |

```{note}
The function parameter `val` is always an unsigned value. The host device
requesting data is interpreting the data as signed or not, the client device
has no informations about it. Setting a holding register to `-4` will be
returned as `65532` on a registered callback.
```

This example functions registered for e.g. coil 123 will output the following
content after the coil has been requested and afterwards set to a different
value

```python
def my_coil_set_cb(reg_type, address, val):
    print('Custom callback, called on setting {} at {} to: {}'.
          format(reg_type, address, val))


def my_coil_get_cb(reg_type, address, val):
    print('Custom callback, called on getting {} at {}, currently: {}'.
          format(reg_type, address, val))


# assuming the client  specific setup (port/ID settings, network connections,
# UART setup) has already been done
# Check the provided examples for further details

# define some registers, for simplicity only a single coil is used
register_definitions = {
    "COILS": {
        "EXAMPLE_COIL": {
            "register": 123,
            "len": 1,
            "val": 0,
            "on_get_cb": my_coil_get_cb,
            "on_set_cb": my_coil_set_cb
        }
    }
}

print('Setting up registers ...')
# use the defined values of each register type provided by register_definitions
client.setup_registers(registers=register_definitions)
# alternatively use dummy default values (True for bool regs, 999 otherwise)
# client.setup_registers(registers=register_definitions, use_default_vals=True)

# callbacks can also be defined after a register setup has been performed
client.add_coil(
    address=123,
    value=bool(1),
    on_set_cb=my_coil_set_cb,
    on_get_cb=my_coil_get_cb
)
print('Register setup done')

while True:
    try:
        result = client.process()
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping TCP client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))
```

```
Setting up registers ...
Register setup done
Custom callback, called on getting COILS at 123, currently: False
Custom callback, called on setting COILS at 123 to: True
```

In case only specific registers shall be enhanced with callbacks the specific
functions can be used individually instead of setting up all registers with the
[`setup_registers`](umodbus.modbus.Modbus.setup_registers) function.

 - [`add_coil`](umodbus.modbus.Modbus.add_coil)
 - [`add_hreg`](umodbus.modbus.Modbus.add_hreg)
 - [`add_ist`](umodbus.modbus.Modbus.add_ist)
 - [`add_ireg`](umodbus.modbus.Modbus.add_ireg)

## Register usage

This section describes the usage of the following implemented functions

 - [0x01 `read_coils`](umodbus.common.CommonModbusFunctions.read_coils)
 - [0x02 `read_discrete_inputs`](umodbus.common.CommonModbusFunctions.read_discrete_inputs)
 - [0x03 `read_holding_registers`](umodbus.common.CommonModbusFunctions.read_holding_registers)
 - [0x04 `read_input_registers`](umodbus.common.CommonModbusFunctions.read_input_registers)
 - [0x05 `write_single_coil`](umodbus.common.CommonModbusFunctions.write_single_coil)
 - [0x06 `write_single_register`](umodbus.common.CommonModbusFunctions.write_single_register)
 - [0x0F `write_multiple_coils`](umodbus.common.CommonModbusFunctions.write_multiple_coils)
 - [0x10 `write_multiple_registers`](umodbus.common.CommonModbusFunctions.write_multiple_registers)

which are available on Modbus RTU and Modbus TCP as shown in the
[GitHub examples folder](https://github.com/brainelectronics/micropython-modbus/tree/develop/examples) and the [examples chapter](EXAMPLES.md)

All described functions require a successful setup of a Host communicating
to/with a Client device which is providing the data and accepting the new data.

### Coils

Coils represent binary states, which can be get as and set to either `0` (off)
or `1` (on).

#### Read

```{note}
The function code `0x01` is used to read from 1 to 2000 contiguous status of
coils in a remote device.
```

With the function
[`read_coils`](umodbus.common.CommonModbusFunctions.read_coils)
a single coil status can be read.

```python
coil_address = 125  # register to start reading
coil_qty = 2        # amount of registers to read

coil_status = host.read_coils(
    slave_addr=slave_addr,
    starting_addr=coil_address,
    coil_qty=coil_qty)

print('Status of COIL {}: {}'.format(coil_address, coil_status))
# Status of COIL 125: [True, False]
```

#### Write

Coils can be set with `False` or `0` to the `OFF` state and with `True` or `1`
to the `ON` state.

##### Single

```{note}
The function code `0x05` is used to write a single output to either `ON` or
`OFF` in a remote device.
```

With the function
[`write_single_coil`](umodbus.common.CommonModbusFunctions.write_single_coil)
a single coil status can be set.

```python
coil_address = 123  # register to start writing
new_coil_val = 0    # new coil value

operation_status = host.write_single_coil(
    slave_addr=slave_addr,
    output_address=coil_address,
    output_value=new_coil_val)

print('Result of setting COIL {}: {}'.format(coil_address, operation_status))
# Result of setting COIL 123: True
```

##### Multiple

```{note}
The function code `0x0F` is used to force each coil in a sequence of coils to
either `ON` or `OFF` in a remote device.
```

With the function
[`write_multiple_coils`](umodbus.common.CommonModbusFunctions.write_multiple_coils)
multiple coil states can be set at once.

```python
coil_address = 126          # register to start writing
new_coil_vals = [1, 1, 0]   # new coil values for 126, 127 and 128

operation_status = host.write_multiple_coils(
            slave_addr=slave_addr,
            starting_address=coil_address,
            output_values=new_coil_vals)

print('Result of setting COIL {}: {}'.format(coil_address, operation_status))
# Result of setting COIL 126: True
```

### Discrete inputs

Discrete inputs represent binary states, which can be get as either `0` (off)
or `1` (on). Unlike [coils](USAGE.md#coils), discrete inputs cannot be set.

#### Read

```{note}
The function code `0x02` is used to read from 1 to 2000 contiguous status of
discrete inputs in a remote device.
```

With the function
[`read_discrete_inputs`](umodbus.common.CommonModbusFunctions.read_discrete_inputs)
discrete inputs can be read.

```python
ist_address = 68    # register to start reading
input_qty = 2       # amount of registers to read

input_status = host.read_discrete_inputs(
    slave_addr=slave_addr,
    starting_addr=ist_address,
    input_qty=input_qty)

print('Status of IST {}: {}'.format(ist_address, input_status))
# Status of IST 68: [True, False]
```

### Holding registers

Holding registers can be get as and set to any value between `0` and `65535`.
If supported by the client device, data can be marked as signed values to
represent `-32768` through `32767`.

#### Read

```{note}
The function code `0x03` is used to read the contents of a contiguous block
of holding registers in a remote device.
```

With the function
[`read_holding_registers`](umodbus.common.CommonModbusFunctions.read_holding_registers)
a single holding register can be read.

```python
hreg_address = 94   # register to start reading
register_qty = 3    # amount of registers to read

register_value = host.read_holding_registers(
    slave_addr=slave_addr,
    starting_addr=hreg_address,
    register_qty=register_qty,
    signed=False)

print('Status of HREG {}: {}'.format(hreg_address, register_value))
# Status of HREG 94: [29, 38, 0]
```

#### Write

Holding registers can be set to `0` through `65535` or `-32768` through `32767`
in case signed values are used.

##### Single

```{note}
The function code `0x06` is used to write a single holding register in a
remote device.
```

With the function
[`write_single_register`](umodbus.common.CommonModbusFunctions.write_single_register)
a single holding register can be set.

```python
hreg_address = 93   # register to start writing
new_hreg_val = 44   # new holding register value

operation_status = host.write_single_register(
    slave_addr=slave_addr,
    register_address=hreg_address,
    register_value=new_hreg_val,
    signed=False)

print('Result of setting HREG {}: {}'.format(hreg_address, operation_status))
# Result of setting HREG 93: True
```

##### Multiple

```{note}
The function code `0x10` is used to write a block of contiguous registers
(1 to 123 registers) in a remote device.
```

With the function
[`write_multiple_registers`](umodbus.common.CommonModbusFunctions.write_multiple_registers)
holding register can be set at once.

```python
hreg_address = 94                   # register to start writing
new_hreg_vals = [54, -12, 30001]    # new holding register values for 94, 95, 96

operation_status = host.write_multiple_registers(
    slave_addr=slave_addr,
    starting_address=hreg_address,
    register_values=new_hreg_vals,
    signed=True)

print('Result of setting HREG {}: {}'.format(hreg_address, operation_status))
# Result of setting HREG 94: True
```

### Input registers

Input registers can hold values between `0` and `65535`. If supported by the
client device, data can be marked as signed values to represent `-32768`
through `32767`. Unlike [holding registers](USAGE.md#holding-registers), input
registers cannot be set.

#### Read

```{note}
The function code `0x04` is used to read from 1 to 125 contiguous input
registers in a remote device.
```

With the function
[`read_input_registers`](umodbus.common.CommonModbusFunctions.read_input_registers)
input registers can be read.

```python
ireg_address = 11   # register to start reading
register_qty = 3    # amount of registers to read

register_value = host.read_input_registers(
    slave_addr=slave_addr,
    starting_addr=ireg_address,
    register_qty=register_qty,
    signed=False)

print('Status of IREG {}: {}'.format(ireg_address, register_value))
# Status of IREG 11: [59123, 0, 390]
```

## TCP

Get two network capable boards up and running, collecting and setting data on
each other.

Adjust the WiFi network name (SSID) and password to be able to connect to your
personal network or remove that section if a wired network connection is used.

### Client

The client, former known as slave, provides some dummy registers which can be
read and updated by another device.

```bash
cp examples/tcp_client_example.py /pyboard/main.py
cp examples/boot.py /pyboard/boot.py
repl
```

Inside the REPL press CTRL+D to perform a soft reboot. The device will serve
several registers now. The log output might look similar to this

```
MPY: soft reboot
System booted successfully!
Waiting for WiFi connection...
Waiting for WiFi connection...
Connected to WiFi.
('192.168.178.69', '255.255.255.0', '192.168.178.1', '192.168.178.1')
Setting up registers ...
Register setup done
Serving as TCP client on 192.168.178.69:502
```

### Host

The host, former known as master, requests and updates some dummy registers of
another device.

```bash
cp examples/tcp_host_example.py /pyboard/main.py
cp examples/boot.py /pyboard/boot.py
repl
```

Inside the REPL press CTRL+D to perform a soft reboot. The device will request
and update registers of the Client after a few seconds. The log output might
look similar to this

```
MPY: soft reboot
System booted successfully!
Waiting for WiFi connection...
Waiting for WiFi connection...
Connected to WiFi.
('192.168.178.42', '255.255.255.0', '192.168.178.1', '192.168.178.1')
Requesting and updating data on TCP client at 192.168.178.69:502

Status of COIL 123: [True]
Result of setting COIL 123: True
Status of COIL 123: [False]

Status of HREG 93: (44,)
Result of setting HREG 93: True
Status of HREG 93: (44,)

Status of IST 67: [False]
Status of IREG 10: (60001,)

Resetting register data to default values...
Result of setting COIL 42: True

Finished requesting/setting data on client
MicroPython v1.18 on 2022-01-17; ESP32 module (spiram) with ESP32
Type "help()" for more information.
>>>
```

## RTU

Get two UART/RS485 capable boards up and running, collecting and setting data
on each other.

Adjust the UART pins according to the MicroPython port specific
[documentation][ref-uart-documentation]. RP2 boards e.g. require the UART pins
as tuple of `Pin`, like `rtu_pins = (Pin(4), Pin(5))` and the specific
`uart_id=1` for those, whereas ESP32 boards can use almost alls pins for UART
communication and shall be given as `rtu_pins = (25, 26)`.

### Client

The client, former known as slave, provides some dummy registers which can be
read and updated by another device.

```bash
cp examples/rtu_client_example.py /pyboard/main.py
cp examples/boot.py /pyboard/boot.py
repl
```

Inside the REPL press CTRL+D to perform a soft reboot. The device will serve
several registers now. The log output might look similar to this

```
MPY: soft reboot
System booted successfully!
Setting up registers ...
Register setup done
Serving as RTU client on address 10 at 9600 baud
```

### Host

The host, former known as master, requests and updates some dummy registers of
another device.

```bash
cp examples/rtu_host_example.py /pyboard/main.py
cp examples/boot.py /pyboard/boot.py
repl
```

Inside the REPL press CTRL+D to perform a soft reboot. The device will request
and update registers of the Client after a few seconds. The log output might
look similar to this

```
MPY: soft reboot
System booted successfully!
Requesting and updating data on RTU client at address 10 with 9600 baud

Status of COIL 123: [True]
Result of setting COIL 123: True
Status of COIL 123: [False]

Status of HREG 93: (44,)
Result of setting HREG 93: True
Status of HREG 93: (44,)

Status of IST 67: [False]
Status of IREG 10: (60001,)

Resetting register data to default values...
Result of setting COIL 42: True

Finished requesting/setting data on client
MicroPython v1.18 on 2022-01-17; ESP32 module (spiram) with ESP32
Type "help()" for more information.
>>>
```

## TCP-RTU bridge

This example implementation shows how to act as bridge between an RTU (serial)
connected device and another external TCP device.

For further details about a TCP-RTU bridge implementation check the header
comment of [`main.py`][ref-package-main-file].

## Classic development environment

This section describes the necessary steps on the computer to read and/or write
data from/to a Modbus TCP Client device.

```bash
# Linux/Mac
source .venv/bin/activate
```

On a Windows based system activate the virtual environment like this

```
.venv\Scripts\activate.bat
```

The onwards mentioned commands shall be performed inside the previously
activated virtual environment.

### TCP

Read and write the Modbus register data from a MicroPython device with the
[brainelectronics ModbusWrapper][ref-github-be-modbus-wrapper] provided with
the [modules submodule][ref-modules-folder]

#### Read data

```bash
python modules/read_device_info_registers.py \
--file=registers/example.json \
--connection=tcp \
--address=192.168.178.69 \
--port=502 \
--print \
--pretty \
--debug \
--verbose=3
```

Or use the even more convenient wrapper script for the wrapper.

```bash
cd examples
sh read_registers_tcp.sh 192.168.178.69 ../registers/example.json 502
```

#### Write data

```bash
python modules/write_device_info_registers.py \
--file=registers/set-example.json \
--connection=tcp \
--address=192.168.178.69 \
--port=502 \
--print \
--pretty \
--debug \
--verbose=3
```

Or use the even more convenient wrapper script for the wrapper.

```bash
cd examples
sh write_registers_tcp.sh 192.168.178.69 ../registers/set-example.json 502
```

<!-- Links -->
[ref-registers-MyEVSE]: https://github.com/brainelectronics/micropython-modbus/blob/c45d6cc334b4adf0e0ffd9152c8f08724e1902d9/registers/modbusRegisters-MyEVSE.json
[ref-myevse-be]: https://brainelectronics.de/
[ref-myevse-tindie]: https://www.tindie.com/stores/brainelectronics/
[ref-package-main-file]: https://github.com/brainelectronics/micropython-modbus/blob/c45d6cc334b4adf0e0ffd9152c8f08724e1902d9/main.py
[ref-uart-documentation]: https://docs.micropython.org/en/latest/library/machine.UART.html
[ref-github-be-modbus-wrapper]: https://github.com/brainelectronics/be-modbus-wrapper
[ref-modules-folder]: https://github.com/brainelectronics/python-modules/tree/43bad716b7db27db07c94c2d279cee57d0c8c753
