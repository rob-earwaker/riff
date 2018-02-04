import io
import struct


class ChunkReadError(Exception):
    pass


class RiffChunkReadError(ChunkReadError):
    pass


class ChunkData(io.RawIOBase):
    def __init__(self, stream, size, startpos):
        self._stream = stream
        self._size = size
        self._startpos = startpos
        self._position = 0
        self._closed = False

    def __repr__(self):
        return 'riff.ChunkData(size={0})'.format(self.size)

    def close(self):
        if not self.closed:
            self._closed = True

    @property
    def closed(self):
        return self._closed or self._stream.closed

    @classmethod
    def create(cls, stream, size):
        startpos = stream.tell() if stream.seekable() else None
        return cls(stream, size, startpos)

    def fileno(self):
        if self.closed:
            raise ValueError('chunk data closed')
        return self._stream.fileno()

    def flush(self):
        if self.closed:
            raise ValueError('chunk data closed')
        pass

    def isatty(self):
        if self.closed:
            raise ValueError('chunk data closed')
        return self._stream.isatty()

    def read(self, size=-1):
        if self.closed:
            raise ValueError('chunk data closed')
        if size < 0:
            return self.readall()
        size = min(size, self.size - self.tell())
        bytestr = self._stream.read(size)
        if bytestr is not None:
            if len(bytestr) == 0 and size != 0:
                raise ChunkReadError('chunk data truncated')
            self._position += len(bytestr)
        return bytestr

    def readable(self):
        if self.closed:
            raise ValueError('chunk data closed')
        return self._stream.readable()

    def readall(self):
        if self.closed:
            raise ValueError('chunk data closed')
        bytestr = b''
        while self.tell() < self.size:
            size = self.size - self.tell()
            readbytes += self.read(size)
            if readbytes is None:
                continue
            bytestr += readbytes
        return bytestr

    def readinto(self, b):
        if self.closed:
            raise ValueError('chunk data closed')
        raise NotImplemented

    def readline(self, size=-1):
        if self.closed:
            raise ValueError('chunk data closed')
        size = min(size, self.size - self.tell())
        line = self._stream.readline(size)
        if len(line) == 0 and size != 0:
            raise ChunkReadError('chunk data truncated')
        self._position += len(line)
        return line

    def readlines(self, hint=-1):
        if self.closed:
            raise ValueError('chunk data closed')
        hint = self.size if hint < 0 else min(hint, self.size)
        lines = []
        while sum(map(len, lines)) < hint:
            lines.append(self.readline())
        return lines

    def seek(self, offset, whence=io.SEEK_SET):
        if self.closed:
            raise ValueError('chunk data closed')
        if not whence in [io.SEEK_SET, io.SEEK_CUR, io.SEEK_END]:
            raise ValueError(
                'invalid whence ({0}, should be {1}, {2} or {3})'.format(
                    whence, io.SEEK_SET, io.SEEK_CUR, io.SEEK_END
                )
            )
        if not self.seekable():
            raise OSError('chunk data is not seekable')
        streampos = self._stream.tell()
        currentpos = self._startpos + self.tell()
        endpos = self._startpos + self.size
        offset = {
            io.SEEK_SET: lambda: self._startpos - streampos + offset,
            io.SEEK_CUR: lambda: currentpos - streampos + offset,
            io.SEEK_END: lambda: endpos - streampos + offset
        }[whence]()
        offset = min(max(offset, self._startpos), endpos)
        streampos = self._stream.seek(offset, io.SEEK_SET)
        if streampos < offset:
            raise ChunkReadError('chunk data truncated')
        self._position = streampos - self._startpos
        return self.tell()

    def seekable(self):
        if self.closed:
            raise ValueError('chunk data closed')
        return self._stream.seekable()

    @property
    def size(self):
        return self._size

    def skip(self):
        if self.closed:
            raise ValueError('chunk data closed')
        endpos = self._startpos + self.size + self.size % 2
        self._stream.seek(endpos)

    def tell(self):
        if self.closed:
            raise ValueError('chunk data closed')
        return self._position

    def truncate(self, size=None):
        if self.closed:
            raise ValueError('chunk data closed')
        raise OSError('chunk data is read-only')

    def writable(self):
        if self.closed:
            raise ValueError('chunk data closed')
        return False

    def write(self, b):
        if self.closed:
            raise ValueError('chunk data closed')
        raise OSError('chunk data is read-only')

    def writelines(self, lines):
        if self.closed:
            raise ValueError('chunk data closed')
        raise OSError('chunk data is read-only')


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
        if not stream.readable():
            raise ChunkReadError('stream is not readable')
        bytestr = stream.read(cls.HEADER_STRUCT.size)
        if len(bytestr) < cls.HEADER_STRUCT.size:
            raise ChunkReadError('header truncated')           
        idbytes, size = cls.HEADER_STRUCT.unpack(bytestr)
        id = idbytes.decode('ascii')
        data = ChunkData.create(stream, size)
        return cls(id, size, data)

    def __repr__(self):
        return "riff.Chunk(id='{0}', size={1})".format(self.id, self.size)


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
        if chunk.id != cls.ID:
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

    def __repr__(self):
        return "riff.RiffChunk(size={0}, format='{1}')".format(
            self.size, self.format
        )
