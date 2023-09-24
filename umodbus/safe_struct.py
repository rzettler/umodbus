# system packages
import struct


def print_error(format, buffer):
    print("  Additional details:")
    print("    format = ", format)
    print("    buffer = ", buffer)
    print("    len(buffer) = ", len(buffer))


def unpack_from(format, buffer, offset):
    try:
        return struct.unpack_from(format, buffer, offset)
    except ValueError as err:
        print("Error unpacking struct:", err)
        print_error(format, buffer)
        print("    offset = ", offset)
        raise


def unpack(format, buffer):
    try:
        return struct.unpack(format, buffer)
    except ValueError as err:
        print("Error unpacking struct:", err)
        print_error(format, buffer)
        raise


def pack(format, *buffer):
    try:
        return struct.pack(format, *buffer)
    except ValueError as err:
        print("Error packing struct:", err)
        print_error(format, buffer)
        raise
