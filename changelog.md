# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [x.y.z] - yyyy-mm-dd
### Added
### Changed
### Removed
### Fixed
-->

<!-- ## [Unreleased] -->

## Released
## [3.0.0] - 2024-07-01
### Added
- Add support for async TCP and RTU client and server, see #5
- Add `CommonRTUFunctions` class to [serial.py](umodbus/serial.py) as an abstract class for use by the RTU client and server
- Add `Async` versions of existing synchronous classes (e.g. `AsyncModbusRTU`, `AsyncTCP`, etc.)

### Changed
- `ists`, `iregs`, `coils` and `hregs` use the type `KeysView` instead of `dict_keys`
- `Serial` class cleaned up, now mainly for requesting data from Modbus RTU masters (e.g. from `ModbusRTU`)
- Refactor examples, now examples need the `common` directory contents to be present as well to run

## [2.3.7] - 2023-07-19
### Fixed
- Add a single character wait time after flush to avoid timing issues with RTU control pin, see #68 and #72

## [2.3.6] - 2023-07-19
### Added
- Add contribution guideline, see #67
- Content of `package.json` is validated on each test workflow run
- Precommit hooks for `package.json` and package version file validation, yaml style, flake8 and trailing whitespace checks, contributes to #67

### Changed
- `umodbus/version.py` file is validated against the latest changelog entry before running all tests and testing the package creation
- `ulogging` placed into `tests` folder instead of installing it with deprecated `upip` in all Docker containers

### Fixed
- Added missing empty line in several files

## [2.3.5] - 2023-07-01
### Fixed
- Time between RS485 control pin raise and UART transmission reduced by 80% from 1000us to 200us
- The RS485 control pin is lowered as fast as possible by using `time.sleep_us()` instead of `machine.idle()` which uses an IRQ on the order of milliseconds. This kept the control pin active longer than necessary, causing the response message to be missed at higher baud rates. This applies only to MicroPython firmwares below v1.20.0
- The following fixes were provided by @wpyoga
- RS485 control pin handling fixed by using UART `flush` function, see #68
- Invalid CRC while reading multiple coils and fixed, see #50 and #52

## [2.3.4] - 2023-03-20
### Added
- `package.json` for `mip` installation with MicroPython v1.19.1 or newer
- `.editorconfig` for common editor settings
- `.yamllint` to lint all used YAML files
- `yamllint` package to the `requirements-test.txt` file
- Run YAML linter on test workflow
- Modbus version input field in issues template

### Changed
- Test workflow is also running on pull requests as the workflow is not executed on branches of contributors

### Fixed
- YAML style violation in Docker, workflow and issue files
- `mip` installation commands in `README` and `INSTALLATION`

## [2.3.3] - 2023-01-29
### Fixed
- Add link to RTU documentation examples from RTU examples files and root [README](README.md), relates to #7
- Add missing ESP32, RP2 and pyboard pin usage for RTU in examples and documentation, relates to #7 and #17
- Add missing issue template file, see #46

## [2.3.2] - 2023-01-09
### Added
- Installation instructions for `mip` usage on MicroPython 1.19.1 or newer, see #44
- [Manual testing Dockerfile](Dockerfile.tests_manually)
- [INSTALLATION](docs/INSTALLATION.md), [TESTING](docs/TESTING.md) and [EXAMPLES](docs/EXAMPLES.md) files for simpler docs structure

### Changed
- Split [SETUP](docs/SETUP.md) into [INSTALLATION](docs/INSTALLATION.md)
- Split [USAGE](docs/USAGE.md) into [TESTING](docs/TESTING.md) and [EXAMPLES](docs/EXAMPLES.md)
- Use callback to reset register data in [RTU client example](examples/rtu_client_example.py)
- Update docs copyright year to 2023
- Use fakes machine module instead of classic Mock in docs config file

### Fixed
- Basic RTU host example in root [README](README.md) uses correct init values, optional parameters are listed after mandatory ones
- Remove outdated warning sections about #35 bug from [USAGE](docs/USAGE.md)

## [2.3.1] - 2023-01-06
### Added
- Unittest to read multiple coils at any location if defined as list, verifies #35
- Unittests to write a single coil or multiple coils at any location if defined as list, verifies fix #15 and #24

### Fixed
- All configured register of a client can be accessed and modified individually, see #35
- Resolved overlapping register positions in example JSON file
- Register length of `EXAMPLE_IREG` in TCP and RTU examples corrected to 1 instead of 2

## [2.3.0] - 2023-01-03
### Added
- Custom callback functions can be registered on client (ModbusRTU or ModbusTCP) side with new parameters `on_set_cb` and `on_get_cb` available from [modbus.py](umodbus/modbus.py) functions `add_coil` and `add_hreg`. Functions `add_ist` and `add_ireg` support only `on_get_cb`, see #31
- Example callback usage shown in [TCP client example](examples/tcp_client_example.py)
- Documentation for callback functions in USAGE

### Changed
- Typing hint `Callable` is now subscriptable

## [2.2.0] - 2023-01-03
### Added
- [Fake machine module](fakes/machine.py) with UART and Pin class to be used on Unix MicroPython container for RTU tests and examples, see #47
- [RTU host example script](examples/rtu_host_example.py)
- [RTU docker compose file](docker-compose-rtu.yaml) and [RTU docker compose file test](docker-compose-rtu-test.yaml) based in MicroPython 1.18 image
- [RTU client Dockerfile](Dockerfile.client_rtu) and [RTU host Dockerfile](Dockerfile.host_rtu) based on MicroPython 1.18 image
- Initial [RTU examples unittest](tests/test_rtu_example.py)
- RTU example section for Client and Host in USAGE

### Changed
- Outsourced the following common functions of [serial.py](umodbus/serial.py) and [tcp.py](umodbus/tcp.py) into `CommonModbusFunctions` of [common.py](umodbus/common.py):
    - `read_coils`
    - `read_discrete_inputs`
    - `read_holding_registers`
    - `read_input_registers`
    - `write_single_coil`
    - `write_single_register`
    - `write_multiple_coils`
    - `write_multiple_registers`

- Inherit from `CommonModbusFunctions` in `Serial` of [serial.py](umodbus/serial.py) and in `TCP` of of [tcp.py](umodbus/tcp.py)
- Extended RTU client example for Docker usage to load all registers from example JSON file
- Update internal functions parameter name from `slave_id` to `slave_addr` of TCP's `_create_mbap_hdr` and `_validate_resp_hdr` function to be the same as in Serial
- Update Modbus function documentation from TCP specific to common module in USAGE file
- Renamed docker files:
     - `Dockerfile.client` -> `Dockerfile.client_tcp`
     - `Dockerfile.host` -> `Dockerfile.host_tcp`
     - `Dockerfile.test_tcp_example` -> `Dockerfile.test_examples`

## [2.1.3] - 2022-12-30
### Fixed
- `uart_id` can be specified during init of `ModbusRTU` and `Serial` class and is no longer hardcoded to `1`, but set as `1` by default to ensure backwards compability, see #7 and #43
- RTU Client example and USAGE documentation updated with new `uart_id` parameter

## [2.1.2] - 2022-12-28
### Changed
- Baudrate specific inter frame time is used at Modbus RTU internal function `_uart_read` of [serial.py](umodbus/serial.py) instead of constant value of 5ms

### Fixed
- ESP32 port specific `wait_tx_done` function replaced by generic wait time calculation in `_send` function of [serial.py](umodbus/serial.py), see #34
- A 1ms delay has been added between turning the RS485 control pin on and sending the Modbus PDU in `_send` function of [serial.py](umodbus/serial.py)

## [2.1.1] - 2022-12-27
### Fixed
- Removed unnecessary dependency to `micropython-urequests` from Docker files, setup guide and package setup file
- Enable Modbus Client mode for RTU implementation, see #40, removed during #33

## [2.1.0] - 2022-12-27
### Added
- Typing hints available for all functions of [umodbus](umodbus), see #27
- Docstrings available for all constants, functions and classes of [umodbus](umodbus/), see #27
- Test for reading more than 8 coils in a row to verify fix of #36
- Test for reading single negative holding register value
- Test for writing multiple coils to verify fix of #22
- Test for writing multiple registers to verify fix of #23
- Usage documentation for coil, discrete inputs, holding register and input register usage
- Modbus TCP IP and port binding can be checked with `is_bound` property in [tcp.py](umodbus/tcp.py)

### Changed
- Reordered modules of API documentation
- `data_as_registers` and `data_as_bits` of [common.py](umodbus/common.py) removed
- Send illegal function code `0x01` if a register other than coil or holding register is requested to be set
- Simplified `_process_write_access` logic of [tcp.py](umodbus/tcp.py)

### Fixed
- Typing hints of function input parameters and return values
- Response data of multiple changed registers (`write_multiple_registers`) is validated with respect to the provided `signed` flag in [serial.py](umodbus/serial.py) and [tcp.py](umodbus/tcp.py), see #23
- Enable reading more than 8 coils in a row, see #36
- Writing multiple coils in TCP, see #22
- Writing multiple registers in TCP, see #23
- Unit test `test_bytes_to_bool` uses MSB and LSB data correctly
- Only requested amount of registers are returned by `_process_read_access` logic of [tcp.py](umodbus/tcp.py), see #35

## [2.0.0] - 2022-12-03
### Added
- Perform MicroPython based unittests on every `Test` workflow run
- Add usage description of docker based MicroPython unittest framework in [USAGE](USAGE.md)
- Add [docker compose file](docker-compose.yaml) based in MicroPython 1.18 image
- Add [TCP client Dockerfile](Dockerfile.client), [TCP host Dockerfile](Dockerfile.host), [unittest Dockerfile](Dockerfile.tests) and [TCP unittest specific Dockerfile](Dockerfile.test_tcp_example). All based on MicroPython 1.18 image
- Add initial test, testing the unittest itself
- Add [unittest](mpy_unittest.py) implementation based on pfalcon's [micropython-unittest](https://github.com/pfalcon/pycopy-lib/blob/56ebf2110f3caa63a3785d439ce49b11e13c75c0/unittest/unittest.py)
- Docstrings available for all functions of [functions.py](umodbus/functions.py), see #27
- Typing hints available for all functions of [functions.py](umodbus/functions.py), [serial.py](umodbus/serial.py) and [tcp.py](umodbus/tcp.py), see #27
- Unittest for [functions.py](umodbus/functions.py), see #16
- Unittest for [const.py](umodbus/const.py), see #16
- [.readthedocs.yaml](.readthedocs.yaml) for Read The Docs, contributes to #26

### Changed
- Use default values for all registers defined in the [example JSON](registers/example.json)
- [TCP host example](examples/tcp_host_example.py) and [TCP client example](examples/tcp_client_example.py) define a static IP address and skip further WiFi setup steps in case a Docker usage is detected by a failing import of the `network` module, contributes to #16
- Define all Modbus function codes as `const()` to avoid external modifications, contributes to #18
- Remove dependency to `Serial` and `requests` from `umodbus.modbus`, see #18
- `ModbusRTU` class is part of [serial.py](umodbus/serial.py), see #18
- `ModbusTCP` class is part of [tcp.py](umodbus/tcp.py), see #18
- `ModbusRTU` and `ModbusTCP` classes and related functions removed from [modbus.py](umodbus/modbus.py), see #18
- Imports changed from:
    - `from umodbus.modbus import ModbusRTU` to `from umodbus.serial import ModbusRTU`
    - `from umodbus.modbus import ModbusTCP` to `from umodbus.tcp import ModbusTCP`
- `read_coils` and `read_discrete_inputs` return a list with the same length as the requested quantity instead of always 8, see #12 and #25
- Common functions `bytes_to_bool` and `to_short` moved to [functions.py](umodbus/functions.py)
- Use HTTPS URL instead of SSH for submodule
- Cleanup of root [README](README.md), content moved to [SETUP](docs/SETUP.md) and [USAGE](docs/USAGE.md), contributes to #30
- Moved [SETUP](docs/SETUP.md) and [USAGE](docs/USAGE.md) into [docs](docs) folder, see #26 contributes to #30
- Use `False` or `0` as default values for registers without a specific initial value in [modbus.py](umodbus/modbus.py)

### Fixed
- `read_coils` returns list with amount of requested coils, see #12
- `read_holding_registers` returns list with amount of requested registers, see #25

## [1.2.0] - 2022-11-13
### Added
- [TCP host example script](examples/tcp_host_example.py)
- JSON file to set registers on TCP/RTU device
- Bash script to wrap manipulation of TCP modbus register data
- [Example boot script](examples/boot.py)
- TOC in [README](README.md)
- Use [changelog-based-release action](https://github.com/brainelectronics/changelog-based-release) to create a draft release with every merge to develop
- Use [changelog-based-release action](https://github.com/brainelectronics/changelog-based-release) to create a drafted prerelease release with every PR build, see #20
- [USAGE](USAGE.md) and [SETUP](SETUP.md) files with more details

### Changed
- Add more info to [TCP client example script](examples/tcp_client_example.py)
- Update [modules submodule](https://github.com/brainelectronics/python-modules/tree/43bad716b7db27db07c94c2d279cee57d0c8c753) to `1.3.0`
- Line breaks are no longer used in this changelog for enumerations
- Issues are referenced as `#123` instead of `[#123][ref-issue-123]` to avoid explicit references at the bottom or some other location in the file
- Scope of contents permissions in release and test release workflow is now `write` to use auto release creation

### Fixed
- Typo in [RTU client example script](examples/rtu_client_example.py)

## [1.1.1] - 2022-11-09
### Fixed
- Default value of `setup_registers` function parameter `use_default_vals`
  changed to `False` to avoid confusion behaviour if not explicitly defined,
  see [issue 13][ref-issue-13]
- Missing function docstring added to `setup_registers` function
- `write_single_coil` allows `0`, `1`, `False`, `True`, `0x0` or `0xFF00`
  instead of `0x0` and `0xFF00` only as set value, see [issue 14][ref-issue-14]

## [1.1.0] - 2022-11-03
### Added
- `float_to_bin`, `bin_to_float`, `int_to_bin` functions added to
  [`umodbus/functions.py`](umodbus/functions.py)
- Deploy to [Test Python Package Index](https://test.pypi.org/) on every PR
  build with a [PEP440][ref-pep440] compliant `-rc<BUILDNUMBER>.dev<PR_NUMBER>`
  meta data extension
- [Test release workflow](.github/workflows/test-release.yaml) running only on
  PRs is archiving and uploading built artifacts to
  [Test Python Package Index](https://test.pypi.org/)

### Changed
- Author is explicitly mentioned in [`setup.py`](setup.py) instead of used by
  `__author__` variable which has been previously defined in
  [`version.py`](umodbus/version.py) but no longer available with autodeploy.

### Fixed
- All uncovered flake8 warnings of [`umodbus`](umodbus)

## [1.0.0] - 2022-02-26
### Added
- [`setup.py`](setup.py) and [`sdist_upip.py`](sdist_upip.py) taken from
  [pfalcon's picoweb repo][ref-pfalcon-picoweb-sdist-upip] and PEP8 improved
- [`MIT License`](LICENSE)
- [`version.py`](umodbus/version.py) storing current library version
- [`typing.py`](umodbus/typing.py) enabling type hints

### Changed
- Moved all uModbus files from `lib/uModbus` into [`umodbus`](umodbus)
- Update import statements of all files of [`umodbus`](umodbus)
- Update [`README`](README.md) usage description of MicroPython lib deploy to
  [PyPi][ref-pypi]
- Usage examples in [`README`](README.md) updated with new import path
- Update [`boot`](boot.py) and [`main`](main.py) files to use `be_helpers`
- Enable setting of `max_connections` to TCP socket in
  [`modbus ModbusTCP bind function`](umodbus/modbus.py) and [`tcp TCPServer bind function`](umodbus/tcp.py)

### Removed
- MicroPython helpers module no longer used
- MicroPython ESP WiFi Manager module no longer used
- Lib folder of dependency modules no longer used
- Commented print debug messages in several files of umodbus

## [0.1.0] - 2022-02-20
### Added
- This changelog file
- [`.gitignore`](.gitignore) file
- [`requirements.txt`](requirements.txt) file to setup tools for board
  interactions
- Creation header to all files of [`lib/uModbus`](lib/uModbus) in order to
  provide proper credits to [Pycom](https://www.pycom.io)
- `get_is_bound()` function added to [`lib/uModbus/tcp.py`](lib/uModbus/tcp.py)
  to check status of socket binding for the Modbus TCP Server (host)
- [Example register files](registers) to show basic usage with a MyEVSE board

### Changed
- Reworked [`boot.py`](boot.py) and [`main.py`](main.py) for simple usage
- [`README`](README.md) file with usage examples
- Replaced WiPy specific calls in [`lib/uModbus`](lib/uModbus) files with
  MicroPython 1.16 or higher calls
- Limit number of concurrent socket connections to the Modbus TCP Server (host)
  to 10
- Return on `_accept_request()` in case of an `OSError` as MicroPython raises
  this type of error in case a socket timeout occured. `TimeoutError` is not
  available on MicroPython compared to WiPy

### Fixed
- PEP8 style issues on all files of [`lib/uModbus`](lib/uModbus)

<!-- Links -->
[Unreleased]: https://github.com/brainelectronics/micropython-modbus/compare/2.3.7...develop

[2.3.7]: https://github.com/brainelectronics/micropython-modbus/tree/2.3.7
[2.3.6]: https://github.com/brainelectronics/micropython-modbus/tree/2.3.6
[2.3.5]: https://github.com/brainelectronics/micropython-modbus/tree/2.3.5
[2.3.4]: https://github.com/brainelectronics/micropython-modbus/tree/2.3.4
[2.3.3]: https://github.com/brainelectronics/micropython-modbus/tree/2.3.3
[2.3.2]: https://github.com/brainelectronics/micropython-modbus/tree/2.3.2
[2.3.1]: https://github.com/brainelectronics/micropython-modbus/tree/2.3.1
[2.3.0]: https://github.com/brainelectronics/micropython-modbus/tree/2.3.0
[2.2.0]: https://github.com/brainelectronics/micropython-modbus/tree/2.2.0
[2.1.3]: https://github.com/brainelectronics/micropython-modbus/tree/2.1.3
[2.1.2]: https://github.com/brainelectronics/micropython-modbus/tree/2.1.2
[2.1.1]: https://github.com/brainelectronics/micropython-modbus/tree/2.1.1
[2.1.0]: https://github.com/brainelectronics/micropython-modbus/tree/2.1.0
[2.0.0]: https://github.com/brainelectronics/micropython-modbus/tree/2.0.0
[1.2.0]: https://github.com/brainelectronics/micropython-modbus/tree/1.2.0
[1.1.1]: https://github.com/brainelectronics/micropython-modbus/tree/1.1.1
[1.1.0]: https://github.com/brainelectronics/micropython-modbus/tree/1.1.0
[1.0.0]: https://github.com/brainelectronics/micropython-modbus/tree/1.0.0
[0.1.0]: https://github.com/brainelectronics/micropython-modbus/tree/0.1.0

[ref-issue-13]: https://github.com/brainelectronics/micropython-modbus/issues/13
[ref-issue-14]: https://github.com/brainelectronics/micropython-modbus/issues/14
[ref-pep440]: https://peps.python.org/pep-0440/
[ref-pypi]: https://pypi.org/
[ref-pfalcon-picoweb-sdist-upip]: https://github.com/pfalcon/picoweb/blob/b74428ebdde97ed1795338c13a3bdf05d71366a0/sdist_upip.py
[ref-be-micropython-module]: https://github.com/brainelectronics/micropython-modules/tree/1.1.0
