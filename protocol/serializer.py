import struct

def write_size_ex(size: int) -> bytes:
    if size < 0xFF:
        return bytes([size])
    else:
        return bytes([0xFF]) + struct.pack('<I', size)

def dump_value(v):
    if v is None:
        return bytes([0x01])
    elif isinstance(v, int):
        if v == 0:  return bytes([0x08])
        if v == 1:  return bytes([0x09])
        if v == -1: return bytes([0x07])
        return bytes([0x04]) + struct.pack('<i', v)
    elif isinstance(v, float):
        return bytes([0x0A]) + struct.pack('<d', v)
    elif isinstance(v, str):
        encoded = v.encode('utf-8')
        if len(encoded) == 0: return bytes([0x0E])
        if len(encoded) == 1: return bytes([0x0F]) + encoded
        return bytes([0x13]) + write_size_ex(len(encoded)) + encoded
    elif isinstance(v, tuple):
        size = len(v)
        if size == 0: header = bytes([0x24])
        elif size == 1: header = bytes([0x25])
        elif size == 2: header = bytes([0x2C])
        else: header = bytes([0x14]) + write_size_ex(size)
        payload = b''.join(dump_value(item) for item in v)
        return header + payload
    elif isinstance(v, dict):
        header = bytes([0x16]) + write_size_ex(len(v))
        payload = b''.join(dump_value(val) + dump_value(k) for k, val in v.items())
        return header + payload
    else:
        raise TypeError(f"Unsupported type: {type(v)}")

def macho_dumps(obj):
    return bytes([0x7E]) + struct.pack('<I', 0) + dump_value(obj)