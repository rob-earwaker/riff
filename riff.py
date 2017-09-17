import io
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


class SeekType:
    FROM_START = 0
    FROM_CURRENT = 1
    FROM_END = 2


class Stream:
    FOUR_CC_STRUCT = struct.Struct('4s')
    UINT_STRUCT = struct.Struct('<I')

    def __init__(self, stream):
        self._stream = stream

    @classmethod
    def from_bytes(cls, bytes):
        return cls.from_stream(io.BytesIO(bytes))

    @classmethod
    def from_stream(cls, stream):
        return stream if isinstance(stream, Stream) else cls(stream)

    def read(self, size):
        bytes = self._stream.read(size)
        missing = size - len(bytes)
        if missing > 0:
            raise UnexpectedEndOfStream(missing, position=self.tell())
        return bytes

    def read_fourcc(self):
        bytes = self.read(4)
        return Stream.FOUR_CC_STRUCT.unpack(bytes)[0].decode('ascii')

    def read_uint(self):
        bytes = self.read(4)
        return Stream.UINT_STRUCT.unpack(bytes)[0]

    def tell(self):
        return self._stream.tell()


class Chunk:
    def __init__(self, id, size, data):
        self._id = id
        self._size = size
        self._data = data

    @classmethod
    def from_stream(cls, stream):
        stream = Stream.from_stream(stream)
        id = stream.read_fourcc()
        size = stream.read_uint()
        data = stream.read(size)
        return cls(id, size, data)

    @property
    def id(self):
        return self._id

    @property
    def size(self):
        return self._size

    @property
    def data(self):
        return self._data


class RiffChunk:
    ID = 'RIFF'

    def __init__(self, size, format, subchunks):
        self._size = size
        self._format = format
        self._subchunks = subchunks

    @classmethod
    def from_stream(cls, stream):
        chunk = Chunk.from_stream(stream)
        if not chunk.id == RiffChunk.ID:
            raise ChunkIdInvalid(actual=chunk.id, expected=RiffChunk.ID)
        data_stream = Stream.from_bytes(chunk.data)
        format = data_stream.read_fourcc()
        subchunks = []
        while data_stream.tell() < chunk.size:
            subchunks.append(Chunk.from_stream(data_stream))
        return cls(chunk.size, format, subchunks)

    @property
    def id(self):
        return RiffChunk.ID

    @property
    def size(self):
        return self._size

    @property
    def format(self):
        return self._format

    def subchunk(self, index):
        return self._subchunks[index]

    def subchunks(self):
        for chunk in self._subchunks:
            yield chunk
