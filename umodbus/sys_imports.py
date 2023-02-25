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

from .typing import List, Optional, Tuple, Union, Literal
from .typing import Callable, Coroutine, Any, KeysView
from .typing import Dict, Awaitable, overload

__all__ = ["machine", "socket", "struct", "time",
           "List", "KeysView", "Optional", "Tuple",
           "Union", "Literal", "Callable", "Coroutine",
           "overload", "Any", "Dict", "Awaitable",
           "UART", "Pin"]
