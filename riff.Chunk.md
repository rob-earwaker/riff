# [`riff`](README.md#riff)`.Chunk`

The [`riff.Chunk`](riff.Chunk.md#riffchunk) type represents a RIFF-formatted chunk, which consists of the following elements:

| Element    | # Bytes    | Format                                                      |
|------------|------------|-------------------------------------------------------------|
| Identifier | 4          | ASCII encoded string                                        |
| Size       | 4          | Little-endian unsigned integer                              |
| Data       | {size}     | Varies, multi-byte integers are assumed to be little-endian |
| Pad        | {size} % 2 | Any (only present if {size} is odd)                         |

The [`riff.Chunk`](riff.Chunk.md#riffchunk) class has the following properties and methods:

- [`riff.Chunk.read`](riff.Chunk.md#riffchunkread)
- [`<riff.Chunk>.id`](riff.Chunk.md#riffchunkid)
- [`<riff.Chunk>.data`](riff.Chunk.md#riffchunkdata)
- [`<riff.Chunk>.size`](riff.Chunk.md#riffchunksize)

## [`riff.Chunk`](riff.Chunk.md#riffchunk)`.read`

The recommended way to create a [`riff.Chunk`](riff.Chunk.md#riffchunk) instance. It reads the chunk identifier and chunk size from a binary IO stream, but does not read beyond the header.

```python
>>> import io
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>> import riff
>>> chunk = riff.Chunk.read(stream)
>>> chunk
riff.Chunk(id='TEST', size=8)
>>> stream.tell()
8
>>>
```

A [`riff.ChunkReadError`](riff.ChunkReadError.md#riffchunkreaderror) will be raised in the following circumstances.

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>> stream.readable = lambda: False
>>> riff.Chunk.read(stream)
Traceback (most recent call last):
  ...
riff.ChunkReadError: stream is not readable
>>>
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

## [`riff.Chunk`](riff.Chunk.md#riffchunk)`.id`

The `id` property of a [`riff.Chunk`](riff.Chunk.md#riffchunk) instance gives the 4-character ASCII string that identifies the chunk type.

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.id
'TEST'
>>>
```

## [`riff.Chunk`](riff.Chunk.md#riffchunk)`.data`

The `data` property of a [`riff.Chunk`](riff.Chunk.md#riffchunk) instance exposes the chunk's data as a stream-like [`riff.ChunkData`](riff.ChunkData.md#riffchunkdata) object, which has size equal to the chunk size.

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data
riff.ChunkData(size=8)
>>>
```

## [`riff.Chunk`](riff.Chunk.md#riffchunk)`.size`

The `size` property of a [`riff.Chunk`](riff.Chunk.md#riffchunk) instance gives the number of bytes of data the chunk contains. This value does not include the 8 byte header, or the pad byte (if applicable).

```python
>>> bytes = b'TEST\x08\x00\x00\x00TestData'#
>>> len(bytes)
16
>>> stream = io.BytesIO(bytes)
>>> chunk = riff.Chunk.read(stream)
>>> chunk.size
8
>>>
>>> bytes = b'TEST\x07\x00\x00\x00OddData\x00'
>>> len(bytes)
16
>>> stream = io.BytesIO(bytes)
>>> chunk = riff.Chunk.read(stream)
>>> chunk.size
7
>>>
```
