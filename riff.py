import struct


class Stream:
    FOUR_CC_STRUCT = struct.Struct('4s')
    UINT_STRUCT = struct.Struct('<I')

    def __init__(self, stream):
        self._stream = stream

    def read(self, size):
        return self._stream.read(size)

    def read_four_cc(self):
        bytestr = self.read(Stream.FOUR_CC_STRUCT.size)
        return Stream.FOUR_CC_STRUCT.unpack(bytestr)[0].decode('ascii')

    def read_uint(self):
        bytestr = self.read(Stream.UINT_STRUCT.size)
        return Stream.UINT_STRUCT.unpack(bytestr)[0]


class Chunk:
    def __init__(self, id, size, data):
        self._id = id
        self._size = size
        self._data = data

    @property
    def id(self):
        return self._id

    @property
    def size(self):
        return self._size

    @property
    def data(self):
        return self._data

    @classmethod
    def read(cls, stream):
        stream = Stream(stream)
        id = stream.read_four_cc()
        size = stream.read_uint()
        return cls(id, size, data=stream)


class RiffChunk:
    ID = 'RIFF'

    def __init__(self, size, format):
        self._size = size
        self._format = format

    @property
    def id(self):
        return RiffChunk.ID

    @property
    def size(self):
        return self._size

    @property
    def format(self):
        return self._format

    @classmethod
    def read(cls, stream):
        chunk = Chunk.read(stream)
        format = chunk.data.read_four_cc()
        return cls(chunk.size, format)
