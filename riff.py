import io
import struct


class Error(Exception):
    pass


class ChunkHeader:
    HEADER_STRUCT = struct.Struct('<4sI')

    def __init__(self, id, size):
        self._id = id
        self._size = size

    @classmethod
    def readfrom(cls, stream):
        buffer = stream.read(cls.HEADER_STRUCT.size)
        if len(buffer) < cls.HEADER_STRUCT.size:
            raise Error('chunk header truncated')
        idbytes, size = cls.HEADER_STRUCT.unpack(buffer)
        try:
            id = idbytes.decode('ascii')
        except UnicodeDecodeError as error:
            raise Error('chunk id not ascii-decodable') from error
        return cls(id, size)

    @property
    def id(self):
        return self._id

    @property
    def size(self):
        return self._size

    def writeto(self, stream):
        idbytes = self.id.encode('ascii')
        buffer = self.HEADER_STRUCT.pack(idbytes, self.size)
        stream.write(buffer)


class ChunkData(io.BufferedIOBase):
    def __init__(self, stream, size, startpos):
        self._stream = stream
        self._size = size
        self._startpos = startpos
        self._position = 0

    @classmethod
    def readfrom(cls, stream, size):
        buffer = stream.read(size)
        if len(buffer) < size:
            raise Error('truncated at position {}'.format(len(buffer)))
        stream = io.BytesIO(buffer)
        return cls(stream, size, startpos=0)

    @classmethod
    def streamfrom(cls, stream, size):
        startpos = stream.seek(0, io.SEEK_CUR)
        stream.seek(size, io.SEEK_CUR)
        return cls(stream, size, startpos)

    def __enter__(self):
        if self.closed:
            raise ValueError('stream closed')
        return super().__enter__()

    def __iter__(self):
        if self.closed:
            raise ValueError('stream closed')
        return super().__iter__()

    def __repr__(self):
        return 'riff.ChunkData(size={0})'.format(self.size)

    @property
    def closed(self):
        return super().closed or self._stream.closed

    def detach(self):
        if self.closed:
            raise ValueError('stream closed')
        raise io.UnsupportedOperation('stream not detachable')

    def fileno(self):
        if self.closed:
            raise ValueError('stream closed')
        return self._stream.fileno()

    def flush(self):
        if self.closed:
            raise ValueError('stream closed')

    def isatty(self):
        if self.closed:
            raise ValueError('stream closed')
        return self._stream.isatty()

    def read(self, size=None):
        self._stream.seek(self._startpos + self.tell(), io.SEEK_SET)
        maxsize = self.size - self.tell()
        size = maxsize if size is None or size < 0 else min(size, maxsize)
        buffer = self._stream.read(size)
        self._position += len(buffer)
        if len(buffer) < size:
            raise Error('truncated at position {}'.format(self.tell()))
        return buffer

    def read1(self, size=None):
        return self.read(size)

    def readable(self):
        if self.closed:
            raise ValueError('stream closed')
        return self._stream.readable()

    def readlines(self, hint=None):
        if self.closed:
            raise ValueError('stream closed')
        return [self.readline()] if hint == 0 else super().readlines(hint)

    def seek(self, offset, whence=io.SEEK_SET):
        if self.closed:
            raise ValueError('stream closed')
        if whence == io.SEEK_SET:
            position = offset
        elif whence == io.SEEK_CUR:
            position = self._position + offset
        elif whence == io.SEEK_END:
            position = self.size + offset
        else:
            raise ValueError('invalid whence value')
        self._position = max(0, min(position, self.size))
        return self._position

    def seekable(self):
        if self.closed:
            raise ValueError('stream closed')
        return self._stream.seekable()

    @property
    def size(self):
        return self._size

    def tell(self):
        return self.seek(0, io.SEEK_CUR)

    def truncate(self, size=None):
        if self.closed:
            raise ValueError('stream closed')
        raise io.UnsupportedOperation('stream not writable')

    def writable(self):
        if self.closed:
            raise ValueError('stream closed')
        return False

    def write(self, buffer):
        if self.closed:
            raise ValueError('stream closed')
        raise io.UnsupportedOperation('stream not writable')

    def writelines(self, lines):
        if self.closed:
            raise ValueError('stream closed')
        raise io.UnsupportedOperation('stream not writable')


class Chunk:
    DEFAULT_PAD_BYTE = b'\x00'
    PAD_SIZE = 1

    def __init__(self, header, data, padbyte):
        self._header = header
        self._data = data
        self._padbyte = padbyte

    @classmethod
    def create(cls, id, size, datastream):
        header = ChunkHeader(id, size)
        data = ChunkData.streamfrom(datastream, size)
        padded = size % 2 != 0
        padbyte = cls.DEFAULT_PAD_BYTE if padded else b''
        return cls(header, data, padbyte)

    @classmethod
    def readfrom(cls, stream):
        header = ChunkHeader.readfrom(stream)
        data = ChunkData.readfrom(stream, header.size)
        padded = header.size % 2 != 0
        padbyte = stream.read(cls.PAD_SIZE) if padded else b''
        return cls(header, data, padbyte)

    @classmethod
    def streamfrom(cls, stream):
        header = ChunkHeader.readfrom(stream)
        data = ChunkData.streamfrom(stream, header.size)
        padded = header.size % 2 != 0
        padbyte = stream.read(cls.PAD_SIZE) if padded else b''
        return cls(header, data, padbyte)

    def __repr__(self):
        return "riff.Chunk(id='{}', size={})".format(self.id, self.size)

    @property
    def data(self):
        return self._data

    @property
    def id(self):
        return self._header.id

    @property
    def padded(self):
        return self.size % 2 != 0

    @property
    def size(self):
        return self._header.size


class RiffChunk:
    FORMAT_STRUCT = struct.Struct('4s')
    ID = 'RIFF'

    def __init__(self, size, format, subchunks):
        self._size = size
        self._format = format
        self._subchunks = subchunks

    @classmethod
    def streamfrom(cls, stream):
        chunk = Chunk.streamfrom(stream)
        if chunk.id != cls.ID:
            raise Error("unexpected chunk id '{}'".format(chunk.id))
        buffer = chunk.data.read(cls.FORMAT_STRUCT.size)
        if len(buffer) < cls.FORMAT_STRUCT.size:
            raise Error('riff chunk format truncated')
        formatbytes, = cls.FORMAT_STRUCT.unpack(buffer)
        try:
            format = formatbytes.decode('ascii')
        except UnicodeDecodeError as error:
            raise Error('riff chunk format not ascii-decodable') from error
        subchunks = []
        while chunk.data.tell() < chunk.data.size:
            subchunk = Chunk.streamfrom(chunk.data)
            subchunks.append(subchunk)
        return cls(chunk.size, format, subchunks)

    @property
    def format(self):
        return self._format

    @property
    def id(self):
        return self.ID

    @property
    def size(self):
        return self._size

    def subchunks(self):
        for subchunk in self._subchunks:
            yield subchunk
