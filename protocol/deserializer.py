"""Full deserializer for EVE marshal format with all opcodes."""

import struct
from typing import Any, Tuple
from protocol.opcodes import PyRepOpcode


class MarshalDeserializer:
    """Deserialize EVE marshal format back to Python objects."""
    
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.string_table = []  # For OpPyStringTableItem
    
    def read_byte(self) -> int:
        """Read a single byte."""
        if self.pos >= len(self.data):
            raise EOFError("Unexpected end of data")
        val = self.data[self.pos]
        self.pos += 1
        return val
    
    def read_uint32(self) -> int:
        """Read 32-bit unsigned integer (little-endian)."""
        if self.pos + 4 > len(self.data):
            raise EOFError("Not enough data for uint32")
        val = struct.unpack('<I', self.data[self.pos:self.pos+4])[0]
        self.pos += 4
        return val
    
    def read_int32(self) -> int:
        """Read 32-bit signed integer (little-endian)."""
        if self.pos + 4 > len(self.data):
            raise EOFError("Not enough data for int32")
        val = struct.unpack('<i', self.data[self.pos:self.pos+4])[0]
        self.pos += 4
        return val
    
    def read_int64(self) -> int:
        """Read 64-bit signed integer (little-endian)."""
        if self.pos + 8 > len(self.data):
            raise EOFError("Not enough data for int64")
        val = struct.unpack('<q', self.data[self.pos:self.pos+8])[0]
        self.pos += 8
        return val
    
    def read_double(self) -> float:
        """Read 64-bit double (little-endian)."""
        if self.pos + 8 > len(self.data):
            raise EOFError("Not enough data for double")
        val = struct.unpack('<d', self.data[self.pos:self.pos+8])[0]
        self.pos += 8
        return val
    
    def read_size_ex(self) -> int:
        """Read variable-length size (for strings, lists, dicts)."""
        first = self.read_byte()
        if first != 0xFF:
            return first
        return self.read_uint32()
    
    def read_string(self) -> str:
        """Read a string (handles OpPyEmptyString, OpPyCharString, OpPyLongString)."""
        opcode = self.read_byte()
        
        if opcode == PyRepOpcode.OpPyEmptyString:
            return ""
        elif opcode == PyRepOpcode.OpPyCharString:
            char = self.read_byte()
            return chr(char)
        elif opcode == PyRepOpcode.OpPyLongString:
            length = self.read_size_ex()
            if self.pos + length > len(self.data):
                raise EOFError(f"String truncated: need {length} bytes")
            raw = self.data[self.pos:self.pos+length]
            self.pos += length
            return raw.decode('utf-8')
        else:
            raise ValueError(f"Expected string opcode, got 0x{opcode:02X}")
    
    def deserialize(self) -> Any:
        """Deserialize the entire stream."""
        # Check header
        if self.read_byte() != PyRepOpcode.MARSHAL_HEADER:
            raise ValueError("Invalid marshal header")
        
        # Read and ignore mapcount (always 0 for root in our usage)
        self.read_uint32()
        
        return self._deserialize_value()
    
    def _deserialize_value(self) -> Any:
        """Deserialize a single value based on its opcode."""
        opcode = self.read_byte()
        
        # None
        if opcode == PyRepOpcode.OpPyNone:
            return None
        
        # Boolean
        elif opcode == PyRepOpcode.OpPyTrue:
            return True
        elif opcode == PyRepOpcode.OpPyFalse:
            return False
        
        # Integers
        elif opcode == PyRepOpcode.OpPyMinusOne:
            return -1
        elif opcode == PyRepOpcode.OpPyZeroInteger:
            return 0
        elif opcode == PyRepOpcode.OpPyOneInteger:
            return 1
        elif opcode == PyRepOpcode.OpPyByte:
            return self.read_byte()
        elif opcode == PyRepOpcode.OpPySignedShort:
            val = self.read_byte() | (self.read_byte() << 8)
            # Sign extend
            if val & 0x8000:
                val -= 0x10000
            return val
        elif opcode == PyRepOpcode.OpPyLong:
            return self.read_int32()
        elif opcode == PyRepOpcode.OpPyLongLong:
            return self.read_int64()
        elif opcode == PyRepOpcode.OpPyVarInteger:
            # Variable-length integer (simplified)
            val = 0
            shift = 0
            while True:
                b = self.read_byte()
                val |= (b & 0x7F) << shift
                shift += 7
                if not (b & 0x80):
                    break
            return val
        
        # Floats
        elif opcode == PyRepOpcode.OpPyZeroReal:
            return 0.0
        elif opcode == PyRepOpcode.OpPyReal:
            return self.read_double()
        
        # Strings
        elif opcode in (PyRepOpcode.OpPyEmptyString, PyRepOpcode.OpPyCharString, 
                        PyRepOpcode.OpPyLongString):
            # Rewind and use read_string
            self.pos -= 1
            return self.read_string()
        
        # Containers
        elif opcode == PyRepOpcode.OpPyEmptyTuple:
            return ()
        elif opcode == PyRepOpcode.OpPyOneTuple:
            return (self._deserialize_value(),)
        elif opcode == PyRepOpcode.OpPyTwoTuple:
            return (self._deserialize_value(), self._deserialize_value())
        elif opcode == PyRepOpcode.OpPyTuple:
            size = self.read_size_ex()
            return tuple(self._deserialize_value() for _ in range(size))
        
        elif opcode == PyRepOpcode.OpPyEmptyList:
            return []
        elif opcode == PyRepOpcode.OpPyOneList:
            return [self._deserialize_value()]
        elif opcode == PyRepOpcode.OpPyList:
            size = self.read_size_ex()
            return [self._deserialize_value() for _ in range(size)]
        
        elif opcode == PyRepOpcode.OpPyDict:
            size = self.read_size_ex()
            result = {}
            for _ in range(size):
                # EVE format: value then key
                value = self._deserialize_value()
                key = self._deserialize_value()
                result[key] = value
            return result
        # В методе _deserialize_value, добавьте эти case:

        elif opcode == PyRepOpcode.OpPyObjectEx1:
            # OpPyObjectEx1 - объект с 1 аргументом
            # Формат: object_id, args
            object_id = self._deserialize_value()
            args = self._deserialize_value()
            return {"__object__": object_id, "args": args}

        elif opcode == PyRepOpcode.OpPyObjectEx2:
            # OpPyObjectEx2 - объект с 2 аргументами
            object_id = self._deserialize_value()
            arg1 = self._deserialize_value()
            arg2 = self._deserialize_value()
            return {"__object__": object_id, "args": (arg1, arg2)}

        elif opcode == PyRepOpcode.OpPyObject:
            # OpPyObject - базовый объект
            object_id = self._deserialize_value()
            return {"__object__": object_id}

        elif opcode == PyRepOpcode.OpPyPackedRow:
            # OpPyPackedRow - упакованная строка данных
            size = self.read_size_ex()
            row_data = self.data[self.pos:self.pos+size]
            self.pos += size
            return {"__packed_row__": row_data}

        elif opcode == PyRepOpcode.OpPySubStream:
            # OpPySubStream - вложенный поток
            size = self.read_size_ex()
            sub_data = self.data[self.pos:self.pos+size]
            self.pos += size
            # Десериализуем подпоток
            sub_deserializer = MarshalDeserializer(sub_data)
            return sub_deserializer.deserialize()
        
        elif opcode == PyRepOpcode.OpPyToken:
            # OpPyToken - ссылка на ранее сериализованный объект
            # Формат: 0x02 + индекс в таблице строк
            token_index = self.read_byte()
            # Для простоты возвращаем заглушку
            # В реальности нужно хранить таблицу строк
            return f"<token_{token_index}>"

        elif opcode == PyRepOpcode.OpPySavedStreamElem:
            # OpPySavedStreamElem - сохранённый элемент потока
            saved_index = self.read_size_ex()
            return f"<saved_stream_elem_{saved_index}>"

        elif opcode == PyRepOpcode.OpPyChecksumedStream:
            # OpPyChecksumedStream - поток с контрольной суммой
            checksum = self.read_uint32()
            size = self.read_size_ex()
            data = self.data[self.pos:self.pos+size]
            self.pos += size
            # Рекурсивно десериализуем содержимое
            sub_parser = MarshalDeserializer(data)
            return sub_parser.deserialize()

        elif opcode == PyRepOpcode.OpPyBuffer:
            # OpPyBuffer - бинарный буфер
            size = self.read_size_ex()
            data = self.data[self.pos:self.pos+size]
            self.pos += size
            return data  # возвращаем как bytes

        elif opcode == PyRepOpcode.OpPyShortString:
            # OpPyShortString - короткая строка (длина 1 байт)
            length = self.read_byte()
            raw = self.data[self.pos:self.pos+length]
            self.pos += length
            return raw.decode('utf-8')

        elif opcode == PyRepOpcode.OpPyWStringUCS2:
            # OpPyWStringUCS2 - UTF-16 строка
            length = self.read_size_ex()
            raw = self.data[self.pos:self.pos+length*2]
            self.pos += length*2
            return raw.decode('utf-16le')

        elif opcode == PyRepOpcode.OpPyWStringUTF8:
            # OpPyWStringUTF8 - UTF-8 строка (современный)
            length = self.read_size_ex()
            raw = self.data[self.pos:self.pos+length]
            self.pos += length
            return raw.decode('utf-8')
        
        else:
            raise NotImplementedError(f"Opcode 0x{opcode:02X} not implemented yet")


def macho_loads(data: bytes) -> Any:
    """Convenience function to deserialize EVE marshal data."""
    deserializer = MarshalDeserializer(data)
    return deserializer.deserialize()