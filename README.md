# `riff`

## `riff.Chunk`

A generic RIFF-formatted chunk is read using the `riff.Chunk.read` class method. This reads the chunk identifier and chunk size from a binary IO stream.

- Chunk identifier: 4 bytes, ASCII encoded string
- Chunk size: 4 bytes, little-endian unsigned integer

For this demonstration, we'll use the [`io`](https://docs.python.org/library/io.html) module from the Python Standard Library to create a stream of bytes in memory, but this could equally be a file stream or any other stream-like object.

```python
>>> import io
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>>
>>> import riff
>>> chunk = riff.Chunk.read(stream)
>>> stream.tell()
8
>>> chunk
riff.Chunk(id='TEST', size=8)
>>>
```

The chunk's data is exposed as a stream-like [`riff.ChunkData`](#riffchunkdata) instance.

```python
>>> chunk.data
riff.ChunkData(size=8)
>>>
```

### Exceptions

Trying to read from a stream that is not readable.

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>> import unittest.mock
>>> stream.readable = unittest.mock.Mock(return_value=False)
>>> riff.Chunk.read(stream)
Traceback (most recent call last):
  ...
riff.ChunkReadError: stream is not readable
>>>
```

Trying to read a chunk with a truncated header.

```python
>>> stream = io.BytesIO(b'TES')
>>> riff.Chunk.read(stream)
Traceback (most recent call last):
  ...
riff.ChunkReadError: header truncated
>>>
>>> stream = io.BytesIO(b'TEST\x04\x00')
>>> riff.Chunk.read(stream)
Traceback (most recent call last):
  ...
riff.ChunkReadError: header truncated
>>>
```

## `riff.ChunkData`

The `riff.ChunkData` type provides a window over a section of the input stream object, where the window starts at the stream position corresponding to the start of the chunk's data and ends after the final byte of chunk data. Note that the end of the chunk data will not necessarily correspond to the end of the input stream, but the `riff.ChunkData` object will still behave as if it had reached the EOF.

A `riff.ChunkData` object has the same interface as a read-only [`io.RawIOBase`](https://docs.python.org/library/io.html#io.RawIOBase) object. It will delegate to the corresponding methods on the input stream in most cases, with additional constraints imposed by the chunk data's start and end positions.

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestDataExtraData')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data
riff.ChunkData(size=8)
>>> chunk.data.read(8)
b'TestData'
>>> stream.tell()
16
>>> chunk.data.tell()
8
>>> chunk.data.read(9)
b''
>>> stream.tell()
16
>>> chunk.data.tell()
8
>>>
```

Note that closing the chunk data stream does not close the input stream, but the `riff.ChunkData` object itself will still behave as if closed.

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.closed
False
>>> chunk.data.read(4)
b'Test'
>>> chunk.data.close()
>>> chunk.data.closed
True
>>> chunk.data.read(4)
Traceback (most recent call last):
  ...
riff.ChunkReadError: chunk data closed
>>>
```

If the input stream is closed, the `riff.ChunkData` object will also behave as if closed.

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.read(4)
b'Test'
>>> stream.close()
>>> chunk.data.closed
True
>>> chunk.data.read(4)
Traceback (most recent call last):
  ...
riff.ChunkReadError: chunk data closed
>>>
```

A chunk's data can be skipped to move the stream position to the end of the data stream.

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestDataExtraData')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.skip()
>>> stream.read(9)
b'ExtraData'
>>>
```

Data is skipped from the current position of the chunk data stream, so will work after reading all or part of the chunk's data.

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestDataExtraData')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.read(4)
b'Test'
>>> chunk.data.skip()
>>> stream.read(9)
b'ExtraData'
>>>
```

Skipping will also skip over the chunk's pad byte if the chunk has an odd number of bytes.

```python
>>> stream = io.BytesIO(b'TEST\x07\x00\x00\x00OddData\x00ExtraData')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.skip()
>>> stream.read(9)
b'ExtraData'
>>>
```

### Exceptions

Trying to read a chunk with truncated data.

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00Test')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.read(4)
b'Test'
>>> chunk.data.read(4)
Traceback (most recent call last):
  ...
riff.ChunkReadError: chunk data truncated
>>>
```

## `riff.RiffChunk`

```python
>>> stream = io.BytesIO(b'RIFF\x04\x00\x00\x00TEST')
>>> riff.RiffChunk.read(stream)
riff.RiffChunk(size=4, format='TEST')
>>> stream.tell()
12
>>>
```

### Exceptions

```python
>>> stream = io.BytesIO(b'TEST\x00\x00\x00\x00')
>>> riff.RiffChunk.read(stream)
Traceback (most recent call last):
  ...
riff.RiffChunkReadError: chunk id 'TEST' != 'RIFF'
>>>
```

```python
>>> stream = io.BytesIO(b'RIFF\x03\x00\x00\x00TES')
>>> riff.RiffChunk.read(stream)
Traceback (most recent call last):
  ...
riff.RiffChunkReadError: chunk size 3 < min size 4
>>>
```
