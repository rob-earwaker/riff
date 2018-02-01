# `riff`

## `riff.Chunk`

To demonstrate reading of a `riff.Chunk` from an IO stream we'll use the [`io`](https://docs.python.org/library/io.html) module from the Python Standard Library to create a stream of bytes in memory, but this could equally be a file stream or any other stream-like object.

```python
>>> import io
>>> stream = io.BytesIO(b'TEST\x0d\x00\x00\x00TestChunkData')
>>>
```

A generic RIFF-formatted chunk is read using the `riff.Chunk.read` class method. This reads the chunk identifier and chunk size from the stream.

- Chunk identifier: 4 bytes, ASCII encoded string
- Chunk size: 4 bytes, little-endian unsigned integer

```python
>>> import riff
>>> chunk = riff.Chunk.read(stream)
>>> stream.tell()
8
>>> chunk.id
'TEST'
>>> chunk.size
13
>>>
```

The chunk data is exposed as a stream-like object.

```python
>>> chunk.data.read(9)
b'TestChunk'
>>> stream.tell()
17
>>> chunk.data.read(4)
b'Data'
>>> stream.tell()
21
>>>
```

### Exceptions

When trying to read a chunk with a truncated chunk identifier.

```python
>>> riff.Chunk.read(io.BytesIO(b'TES'))
Traceback (most recent call last):
  ...
riff.ChunkReadError: chunk id truncated
>>>
```

When trying to read a chunk with a truncated chunk size.

```python
>>> riff.Chunk.read(io.BytesIO(b'TEST\x0d\x00\x00'))
Traceback (most recent call last):
  ...
riff.ChunkReadError: chunk size truncated
>>>
```

## `riff.RiffChunk`

```python
>>> stream = io.BytesIO(b'RIFF\x04\x00\x00\x00TEST')
>>> riff_chunk = riff.RiffChunk.read(stream)
>>> riff_chunk.id
'RIFF'
>>> riff_chunk.size
4
>>> riff_chunk.format
'TEST'
>>> stream.tell()
12
>>>
```

### Exceptions

```python
>>> riff.RiffChunk.read(io.BytesIO(b'TEST\x00\x00\x00\x00'))
Traceback (most recent call last):
  ...
riff.RiffChunkReadError: chunk id 'TEST' != 'RIFF'
>>>
```

```python
>>> riff.RiffChunk.read(io.BytesIO(b'RIFF\x03\x00\x00\x00TES'))
Traceback (most recent call last):
  ...
riff.RiffChunkReadError: chunk size 3 < min size 4
>>>
```

```python
>>> riff.RiffChunk.read(io.BytesIO(b'RIFF\x04\x00\x00\x00TE'))
Traceback (most recent call last):
  ...
riff.RiffChunkReadError: chunk format truncated
>>>
```