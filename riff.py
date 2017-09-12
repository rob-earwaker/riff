import struct


class UnexpectedEndOfStream(Exception):
    def __init__(self, missing, position):
        message_format = 'Expected {0} more byte(s) after position {1}'
        message = message_format.format(missing, position)
        super().__init__(message)


class ChunkIdInvalid(Exception):
    def __init__(self, actual, expected):
        message = '{0} != {1}'.format(actual, expected)
        super().__init__(message)


class RiffStream:
    FOUR_CC_STRUCT = struct.Struct('4s')
    UINT_STRUCT = struct.Struct('<I')

    def __init__(self, stream):
        self._stream = stream

    @classmethod
    def from_stream(cls, stream):
        return stream if isinstance(stream, RiffStream) else cls(stream)

    def read(self, size):
        bytes = self._stream.read(size)
        missing = size - len(bytes)
        if missing > 0:
            raise UnexpectedEndOfStream(missing, position=self._stream.tell())
        return bytes

    def read_fourcc(self):
        bytes = self.read(4)
        return RiffStream.FOUR_CC_STRUCT.unpack(bytes)[0].decode('ascii')

    def read_uint(self):
        bytes = self.read(4)
        return RiffStream.UINT_STRUCT.unpack(bytes)[0]


class RiffChunk:
    ID = 'RIFF'

    def __init__(self, size, format, data):
        self._size = size
        self._format = format
        self._data = data

    @classmethod
    def from_stream(cls, stream):
        stream = RiffStream.from_stream(stream)
        id = stream.read_fourcc()
        if not id == RiffChunk.ID:
            raise ChunkIdInvalid(actual=id, expected=RiffChunk.ID)
        size = stream.read_uint()
        format = stream.read_fourcc()
        data = stream.read(size - RiffStream.FOUR_CC_STRUCT.size)
        return cls(size, format, data)

    @property
    def id(self):
        return RiffChunk.ID

    @property
    def size(self):
        return self._size

    @property
    def format(self):
        return self._format

    @property
    def data(self):
        return self._data
