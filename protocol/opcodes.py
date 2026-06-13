"""PyRep opcodes from EVE Online marshal format."""

from enum import IntEnum


class PyRepOpcode(IntEnum):
    """6-bit opcodes in the marshal stream."""
    
    OpPyNone             = 0x01
    OpPyToken            = 0x02
    OpPyLongLong         = 0x03
    OpPyLong             = 0x04
    OpPySignedShort      = 0x05
    OpPyByte             = 0x06
    OpPyMinusOne         = 0x07
    OpPyZeroInteger      = 0x08
    OpPyOneInteger       = 0x09
    OpPyReal             = 0x0A
    OpPyZeroReal         = 0x0B
    OpPyBuffer           = 0x0D
    OpPyEmptyString      = 0x0E
    OpPyCharString       = 0x0F
    OpPyShortString      = 0x10
    OpPyStringTableItem  = 0x11
    OpPyWStringUCS2      = 0x12
    OpPyLongString       = 0x13
    OpPyTuple            = 0x14
    OpPyList             = 0x15
    OpPyDict             = 0x16
    OpPyObject           = 0x17
    OpPySubStruct        = 0x19
    OpPySavedStreamElem  = 0x1B
    OpPyChecksumedStream = 0x1C
    OpPyTrue             = 0x1F
    OpPyFalse            = 0x20
    OpCPicked            = 0x21
    OpPyObjectEx1        = 0x22
    OpPyObjectEx2        = 0x23
    OpPyEmptyTuple       = 0x24
    OpPyOneTuple         = 0x25
    OpPyEmptyList        = 0x26
    OpPyOneList          = 0x27
    OpPyEmptyWString     = 0x28
    OpPyWStringUCS2Char  = 0x29
    OpPyPackedRow        = 0x2A
    OpPySubStream        = 0x2B
    OpPyTwoTuple         = 0x2C
    OpPackedTerminator   = 0x2D
    OpPyWStringUTF8      = 0x2E
    OpPyVarInteger       = 0x2F
    
    # Masks and constants
    OPCODE_MASK          = 0x3F
    SAVE_MASK            = 0x40
    UNKNOWN_MASK         = 0x80
    MARSHAL_HEADER       = 0x7E  # '~'


# Aliases for convenience (matching EVE naming)
OP_NONE = PyRepOpcode.OpPyNone
OP_TOKEN = PyRepOpcode.OpPyToken
OP_LONG_LONG = PyRepOpcode.OpPyLongLong
OP_LONG = PyRepOpcode.OpPyLong
OP_SIGNED_SHORT = PyRepOpcode.OpPySignedShort
OP_BYTE = PyRepOpcode.OpPyByte
OP_MINUS_ONE = PyRepOpcode.OpPyMinusOne
OP_ZERO_INT = PyRepOpcode.OpPyZeroInteger
OP_ONE_INT = PyRepOpcode.OpPyOneInteger
OP_REAL = PyRepOpcode.OpPyReal
OP_ZERO_REAL = PyRepOpcode.OpPyZeroReal
OP_BUFFER = PyRepOpcode.OpPyBuffer
OP_EMPTY_STRING = PyRepOpcode.OpPyEmptyString
OP_CHAR_STRING = PyRepOpcode.OpPyCharString
OP_SHORT_STRING = PyRepOpcode.OpPyShortString
OP_STRING_TABLE_ITEM = PyRepOpcode.OpPyStringTableItem
OP_WSTRING_UCS2 = PyRepOpcode.OpPyWStringUCS2
OP_LONG_STRING = PyRepOpcode.OpPyLongString
OP_TUPLE = PyRepOpcode.OpPyTuple
OP_LIST = PyRepOpcode.OpPyList
OP_DICT = PyRepOpcode.OpPyDict
OP_OBJECT = PyRepOpcode.OpPyObject
OP_SUB_STRUCT = PyRepOpcode.OpPySubStruct
OP_SAVED_STREAM_ELEM = PyRepOpcode.OpPySavedStreamElem
OP_CHECKSUMED_STREAM = PyRepOpcode.OpPyChecksumedStream
OP_TRUE = PyRepOpcode.OpPyTrue
OP_FALSE = PyRepOpcode.OpPyFalse
OP_CPICKED = PyRepOpcode.OpCPicked
OP_OBJECT_EX1 = PyRepOpcode.OpPyObjectEx1
OP_OBJECT_EX2 = PyRepOpcode.OpPyObjectEx2
OP_EMPTY_TUPLE = PyRepOpcode.OpPyEmptyTuple
OP_ONE_TUPLE = PyRepOpcode.OpPyOneTuple
OP_EMPTY_LIST = PyRepOpcode.OpPyEmptyList
OP_ONE_LIST = PyRepOpcode.OpPyOneList
OP_EMPTY_WSTRING = PyRepOpcode.OpPyEmptyWString
OP_WSTRING_UCS2_CHAR = PyRepOpcode.OpPyWStringUCS2Char
OP_PACKED_ROW = PyRepOpcode.OpPyPackedRow
OP_SUB_STREAM = PyRepOpcode.OpPySubStream
OP_TWO_TUPLE = PyRepOpcode.OpPyTwoTuple
OP_PACKED_TERMINATOR = PyRepOpcode.OpPackedTerminator
OP_WSTRING_UTF8 = PyRepOpcode.OpPyWStringUTF8
OP_VAR_INTEGER = PyRepOpcode.OpPyVarInteger