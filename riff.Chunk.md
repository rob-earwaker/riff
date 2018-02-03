# `riff.Chunk`

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

## Exceptions

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
