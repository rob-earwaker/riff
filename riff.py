import struct


FOUR_CC_STRUCT = struct.Struct('4s')


class ChunkReadError(Exception):
    pass


class RiffChunkReadError(ChunkReadError):
    pass


class Chunk:
    ID_STRUCT = FOUR_CC_STRUCT
    SIZE_STRUCT = struct.Struct('<I')

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
        bytestr = stream.read(cls.ID_STRUCT.size)
        if len(bytestr) < cls.ID_STRUCT.size:
            raise ChunkReadError('chunk id truncated')           
        id = cls.ID_STRUCT.unpack(bytestr)[0].decode('ascii')

        bytestr = stream.read(cls.SIZE_STRUCT.size)
        if len(bytestr) < cls.SIZE_STRUCT.size:
            raise ChunkReadError('chunk size truncated')
        size = cls.SIZE_STRUCT.unpack(bytestr)[0]

        return cls(id, size, data=stream)


class RiffChunk:
    ID = 'RIFF'
    FORMAT_STRUCT = FOUR_CC_STRUCT
    MIN_CHUNK_SIZE = FORMAT_STRUCT.size

    def __init__(self, size, format):
        self._size = size
        self._format = format

    @property
    def id(self):
        return self.ID

    @property
    def size(self):
        return self._size

    @property
    def format(self):
        return self._format

    @classmethod
    def read(cls, stream):
        chunk = Chunk.read(stream)
        if not chunk.id == cls.ID:
            raise RiffChunkReadError(
                "chunk id '{0}' != '{1}'".format(chunk.id, cls.ID)
            )
        if chunk.size < cls.MIN_CHUNK_SIZE:
            raise RiffChunkReadError(
                'chunk size {0} < {1}'.format(chunk.size, cls.MIN_CHUNK_SIZE)
            )

        bytestr = chunk.data.read(cls.FORMAT_STRUCT.size)
        if len(bytestr) < cls.FORMAT_STRUCT.size:
            raise RiffChunkReadError('chunk format truncated')
        format = cls.FORMAT_STRUCT.unpack(bytestr)[0].decode('ascii')

        return cls(chunk.size, format)
