# `riff`

## `riff.Chunk`

A generic RIFF-formatted chunk is read using the `riff.Chunk.read` class method. This reads the chunk identifier and chunk size from an IO stream.

- Chunk identifier: 4 bytes, ASCII encoded string
- Chunk size: 4 bytes, little-endian unsigned integer

For this demonstration, we'll use the [`io`](https://docs.python.org/library/io.html) module from the Python Standard Library to create a stream of bytes in memory, but this could equally be a file stream or any other stream-like object.

```python
>>> import io
>>> stream = io.BytesIO(b'TEST\x0d\x00\x00\x00TestChunkData')
>>>
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
>>> chunk.data.size
13
>>> stream.tell()
8
>>> chunk.data.tell()
0
>>> chunk.data.read(9)
b'TestChunk'
>>> chunk.data.tell()
9
>>> chunk.data.read(4)
b'Data'
>>>
```

The chunk data stream will prevent you reading beyond the number of bytes specified by the chunk size, even if the source stream contains more data.

```python
>>> stream = io.BytesIO(b'TEST\x0d\x00\x00\x00TestChunkDataExtraData')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.read(13)
b'TestChunkData'
>>> chunk.data.tell()
13
>>> chunk.data.read(9)
b''
>>> chunk.data.tell()
13
>>>
```

### Exceptions

Trying to read a chunk with a truncated chunk identifier.

```python
>>> stream = io.BytesIO(b'TES')
>>> riff.Chunk.read(stream)
Traceback (most recent call last):
  ...
riff.ChunkReadError: chunk id truncated
>>>
```

Trying to read a chunk with a truncated chunk size.

```python
>>> stream = io.BytesIO(b'TEST\x0d\x00\x00')
>>> riff.Chunk.read(stream)
Traceback (most recent call last):
  ...
riff.ChunkReadError: chunk size truncated
>>>
```

Trying to read a chunk with truncated data.

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00DATA')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.read(4)
b'DATA'
>>> chunk.data.read(4)
Traceback (most recent call last):
  ...
riff.ChunkReadError: chunk data truncated
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
