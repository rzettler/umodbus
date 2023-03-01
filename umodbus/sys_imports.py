#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Common library imports class

Used to handle imports across different platforms, which may have packages
named differently (e.g. due to a lack of aliasing), or be missing entirely
such as :py:module:`machine`, which is missing from the Ubuntu MicroPython
port.
"""

try:
    import usocket as socket
    import ustruct as struct
    import utime as time
except ImportError:
    import socket
    import struct
    import time

try:
    import machine
    from machine import UART, Pin
except ImportError:
    class __unresolved_import:
        pass

    machine = __unresolved_import()
    Pin = __unresolved_import()
    UART = __unresolved_import()

try:
    from typing import List, Optional, Tuple, Union, Literal
    from typing import Callable, Coroutine, Any, KeysView
    from typing import Dict, Awaitable, overload
except ImportError:
    from .typing import List, Optional, Tuple, Union, Literal
    from .typing import Callable, Coroutine, Any, KeysView
    from .typing import Dict, Awaitable, overload

__all__ = ["machine", "socket", "struct", "time",
           "List", "KeysView", "Optional", "Tuple",
           "Union", "Literal", "Callable", "Coroutine",
           "overload", "Any", "Dict", "Awaitable",
           "UART", "Pin"]
