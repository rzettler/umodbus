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
    from typing import Dict, Awaitable
except ImportError:
    # typing not natively supported on MicroPython
    from .typing import List, Optional, Tuple, Union, Literal
    from .typing import Callable, Coroutine, Any, KeysView
    from .typing import Dict, Awaitable

__all__ = ["machine", "socket", "struct", "time",
           "List", "KeysView", "Optional", "Tuple",
           "Union", "Literal", "Callable", "Coroutine",
           "Any", "Dict", "Awaitable", "UART",
           "Pin"]