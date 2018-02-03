# [`riff.Chunk`](#riff.Chunk.md#riffchunk)

The [`riff.Chunk`](#riff.Chunk.md#riffchunk) type represents a RIFF-formatted chunk, which consists of the following elements:

| Element    | # Bytes    | Format                                                      |
|------------|------------|-------------------------------------------------------------|
| Identifier | 4          | ASCII encoded string                                        |
| Size       | 4          | Little-endian unsigned integer                              |
| Data       | {size}     | Varies, multi-byte integers are assumed to be little-endian |
| Pad        | {size} % 2 | Any (only present if {size} is odd)                         |

The [`riff.Chunk`](#riff.Chunk.md#riffchunk) class has the following properties and methods:

- [`riff.Chunk.read`](#riff.Chunk.md#riffchunkread)
- `<riff.Chunk>.id`
- `<riff.Chunk>.size`
- `<riff.Chunk>.data`

## [`riff.Chunk.read`](#riff.Chunk.md#riffchunkread)

The recommended way to create a [`riff.Chunk`](#riff.Chunk.md#riffchunk) instance. It reads the chunk identifier and chunk size from a binary IO stream, but does not read beyond the header.

```python
>>> import io
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>>
>>> import riff
>>> chunk = riff.Chunk.read(stream)
>>> chunk
riff.Chunk(id='TEST', size=8)
>>> stream.tell()
8
>>>
```

A [`riff.ChunkReadError`](#riff.ChunkReadError.md#riffchunkreaderror) will be raised in the following circumstances.

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
