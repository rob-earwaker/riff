import io
import struct


class Error(Exception):
    pass


class ChunkData:
    def __init__(self, stream, size):
        self._stream = stream
        self._size = size
        self._position = 0

    def __repr__(self):
        return 'riff.ChunkData(size={0})'.format(self.size)

    @property
    def consumed(self):
        return self.position == self.size

    @property
    def position(self):
        return self._position

    @property
    def size(self):
        return self._size

    def read(self, size):
        size = max(size, 0)
        size = min(size, self.size - self.position)
        bytestr = self._stream.read(size)
        self._position += len(bytestr)
        if len(bytestr) < size:
            raise Error('chunk data truncated')
        return bytestr

    def readall(self):
        size = self.size - self.position
        return self.read(size)

    def readover(self, size, buffersize=1024):
        size = max(size, 0)
        size = min(size, self.size - self.position)
        endpos = self.position + size
        while self.position < endpos:
            size = min(buffersize, endpos - self.position)
            self.read(size)

    def readoverall(self, buffersize=1024):
        size = self.size - self.position
        self.readover(size, buffersize)

    def skip(self, size):
        offset = max(size, 0)
        offset = min(offset, self.size - self.position)
        try:
            self._stream.seek(offset, io.SEEK_CUR)
        except (AttributeError, OSError) as error:
            raise Error('stream is not seekable') from error
        self._position += offset

    def skipall(self):
        size = self.size - self.position
        self.skip(size)


class Chunk:
    HEADER_STRUCT = struct.Struct('<4sI')
    PAD_SIZE = 1

    def __init__(self, id, data, stream, expectpadbyte):
        self._id = id
        self._data = data
        self._stream = stream
        self._expectpadbyte = expectpadbyte
        self._padconsumed = False
        self._position = 0

    @classmethod
    def create(cls, id, size, datastream):
        data = ChunkData(datastream, size)
        return cls(id, data, stream=datastream, expectpadbyte=False)

    @classmethod
    def readfrom(cls, stream):
        bytestr = stream.read(cls.HEADER_STRUCT.size)
        if len(bytestr) < cls.HEADER_STRUCT.size:
            raise Error('chunk header truncated')
        idbytes, size = cls.HEADER_STRUCT.unpack(bytestr)
        try:
            id = idbytes.decode('ascii')
        except UnicodeDecodeError as error:
            raise Error('chunk id not ascii-decodable') from error
        data = ChunkData(stream, size)
        return cls(id, data, stream, expectpadbyte=True)

    @property
    def consumed(self):
        return self.data.consumed and (not self.padded or self._padconsumed)

    @property
    def data(self):
        return self._data

    @property
    def id(self):
        return self._id

    @property
    def padded(self):
        return self.size % 2 != 0

    def readover(self, buffersize=1024):
        self.data.readoverall(buffersize)
        self.readpadbyte()

    def readpadbyte(self):
        if not self.data.consumed:
            raise Error('not all chunk data has been consumed')
        if not self.padded or self._padconsumed:
            return b''
        if not self._expectpadbyte:
            padbyte = b'\x00'
        else:
            padbyte = self._stream.read(self.PAD_SIZE)
            if len(padbyte) < self.PAD_SIZE:
                raise Error('chunk truncated - expected pad byte')
        self._padconsumed = True
        return padbyte

    @property
    def size(self):
        return self.data.size

    def skip(self):
        self.data.skipall()
        self.skippadbyte()

    def skippadbyte(self):
        if not self.data.consumed:
            raise Error('not all chunk data has been consumed')
        if not self.padded or self._padconsumed:
            return
        if self._expectpadbyte:
            try:
                self._stream.seek(self.PAD_SIZE, io.SEEK_CUR)
            except (AttributeError, OSError) as error:
                raise Error('stream is not seekable') from error
        self._padconsumed = True

    def writeto(self, stream, buffersize=1024):
        if self.data.position != 0:
            raise Error('chunk partially consumed')
        idbytes = self.id.encode('ascii')
        headerbytes = self.HEADER_STRUCT.pack(idbytes, self.size)
        stream.write(headerbytes)
        self.data.writeto(stream, buffersize)
        if self.padded:
            padbyte = self.readpadbyte()
            stream.write(padbyte)

    def __repr__(self):
        return "riff.Chunk(id='{}', size={})".format(self.id, self.size)


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
            raise Error("chunk id '{0}' != '{1}'".format(chunk.id, cls.ID))
        if chunk.size < cls.MIN_CHUNK_SIZE:
            raise Error(
                'chunk size {0} < min size {1}'.format(
                    chunk.size, cls.MIN_CHUNK_SIZE
                )
            )
        bytestr = chunk.data.read(cls.FORMAT_STRUCT.size)
        if len(bytestr) < cls.FORMAT_STRUCT.size:
            raise Error('chunk format truncated')
        format = cls.FORMAT_STRUCT.unpack(bytestr)[0].decode('ascii')
        return cls(chunk.size, format)

    def __repr__(self):
        return "riff.RiffChunk(size={0}, format='{1}')".format(
            self.size, self.format
        )
