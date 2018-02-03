import struct


class ChunkReadError(Exception):
    pass


class RiffChunkReadError(ChunkReadError):
    pass


class ChunkData:
    def __init__(self, stream, startpos, size):
        self._stream = stream
        self._startpos = startpos
        self._size = size

    @property
    def size(self):
        return self._size

    @classmethod
    def create(cls, stream, size):
        startpos = stream.tell()
        return cls(stream, startpos, size)

    def tell(self):
        return self._stream.tell() - self._startpos

    def read(self, size):
        size = min(size, self._size - self.tell())
        bytestr = self._stream.read(size)
        if len(bytestr) < size:
            raise ChunkReadError('chunk data truncated')
        return bytestr

    def skip(self):
        endpos = self._startpos + self.size + self.size % 2
        self._stream.seek(endpos)


class Chunk:
    HEADER_STRUCT = struct.Struct('<4sI')

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
        bytestr = stream.read(cls.HEADER_STRUCT.size)
        if len(bytestr) < cls.HEADER_STRUCT.size:
            raise ChunkReadError('header truncated')           
        idbytes, size = cls.HEADER_STRUCT.unpack(bytestr)
        id = idbytes.decode('ascii')
        data = ChunkData.create(stream, size)
        return cls(id, size, data)


class RiffChunk:
    ID = 'RIFF'
    FORMAT_STRUCT = struct.Struct('4s')
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
                'chunk size {0} < min size {1}'.format(
                    chunk.size, cls.MIN_CHUNK_SIZE
                )
            )

        bytestr = chunk.data.read(cls.FORMAT_STRUCT.size)
        if len(bytestr) < cls.FORMAT_STRUCT.size:
            raise RiffChunkReadError('chunk format truncated')
        format = cls.FORMAT_STRUCT.unpack(bytestr)[0].decode('ascii')

        return cls(chunk.size, format)
