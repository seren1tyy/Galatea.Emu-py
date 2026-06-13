import struct
from protocol.opcodes import (
    PyRepOpcode, OP_NONE, OP_LONG, OP_MINUS_ONE, OP_ZERO_INT, OP_ONE_INT,
    OP_REAL, OP_EMPTY_STRING, OP_CHAR_STRING, OP_LONG_STRING,
    OP_TUPLE, OP_EMPTY_TUPLE, OP_ONE_TUPLE, OP_TWO_TUPLE,
    OP_DICT
)


def write_size_ex(size: int) -> bytes:
    """Write variable-length integer (for strings, lists, dicts)."""
    if size < 0xFF:
        return bytes([size])
    else:
        return bytes([0xFF]) + struct.pack('<I', size)


def dump_value(v):
    """Serialize a Python value to EVE marshal format."""
    
    if v is None:
        return bytes([OP_NONE])
    
    elif isinstance(v, bool):
        return bytes([PyRepOpcode.OpPyTrue if v else PyRepOpcode.OpPyFalse])
    
    elif isinstance(v, int):
        if v == -1:
            return bytes([OP_MINUS_ONE])
        if v == 0:
            return bytes([OP_ZERO_INT])
        if v == 1:
            return bytes([OP_ONE_INT])
        # Для больших чисел используем OpPyLong
        return bytes([OP_LONG]) + struct.pack('<i', v)
    
    elif isinstance(v, float):
        if v == 0.0:
            return bytes([PyRepOpcode.OpPyZeroReal])
        return bytes([OP_REAL]) + struct.pack('<d', v)
    
    elif isinstance(v, str):
        encoded = v.encode('utf-8')
        if len(encoded) == 0:
            return bytes([OP_EMPTY_STRING])
        elif len(encoded) == 1:
            return bytes([OP_CHAR_STRING]) + encoded
        else:
            return bytes([OP_LONG_STRING]) + write_size_ex(len(encoded)) + encoded
    
    elif isinstance(v, (tuple, list)):
        size = len(v)
        
        if isinstance(v, tuple):
            if size == 0:
                header = bytes([OP_EMPTY_TUPLE])
            elif size == 1:
                header = bytes([OP_ONE_TUPLE])
            elif size == 2:
                header = bytes([OP_TWO_TUPLE])
            else:
                header = bytes([OP_TUPLE]) + write_size_ex(size)
        else:  # list
            if size == 0:
                header = bytes([PyRepOpcode.OpPyEmptyList])
            elif size == 1:
                header = bytes([PyRepOpcode.OpPyOneList])
            else:
                header = bytes([PyRepOpcode.OpPyList]) + write_size_ex(size)
        
        payload = b''.join(dump_value(item) for item in v)
        return header + payload
    
    elif isinstance(v, dict):
        header = bytes([OP_DICT]) + write_size_ex(len(v))
        # ВАЖНО: EVE формат: сначала значения, потом ключи
        # И ключи должны быть строками!
        payload = b''
        for key, val in v.items():
            # Убеждаемся, что ключ - строка
            if not isinstance(key, str):
                key = str(key)
            payload += dump_value(val) + dump_value(key)
        return header + payload
    
    else:
        raise TypeError(f"Unsupported type for serialization: {type(v)} (value: {v})")


def macho_dumps(obj) -> bytes:
    """
    Serialize object to EVE marshal format with header.
    
    Format: 0x7E + mapcount (4 bytes, zero for root) + data
    """
    return bytes([PyRepOpcode.MARSHAL_HEADER]) + struct.pack('<I', 0) + dump_value(obj)