#!/usr/bin/env python
#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#
# compatibility for ports which do not have inet_ntop available

try:
    from socket import inet_ntop
except ImportError:
    def inet_ntop(packed_ip: bytes) -> str:
        return ".".join(map(str, packed_ip))
