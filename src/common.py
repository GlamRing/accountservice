import struct


def raise_(ex):
    raise ex


def to_bytes(value, size=1, endian='>'):
    return {
        1: lambda: struct.pack(endian + 'B', value),
        2: lambda: struct.pack(endian + 'H', value),
        4: lambda: struct.pack(endian + 'I', value)
    }.get(size, lambda: raise_(RuntimeErro