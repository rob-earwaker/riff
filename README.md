# `riff`

## `riff.Chunk`

```python
>>> import io
>>> stream = io.BytesIO(b'TEST\x0d\x00\x00\x00TestChunkData')
>>>
```

```python
>>> import riff
>>> chunk = riff.Chunk.read(stream)
>>> chunk.id
'TEST'
>>> chunk.size
13
>>> stream.tell()
8
>>> chunk.data.read(13)
b'TestChunkData'
>>>
```

### Exceptions

```python
>>> riff.Chunk.read(io.BytesIO(b'TES'))
Traceback (most recent call last):
  ...
riff.ChunkReadError: chunk id truncated
>>>
```

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
>>> riff.RiffChunk.read(io.BytesIO(b'RIFF\x00\x00\x00\x00'))
Traceback (most recent call last):
  ...
riff.RiffChunkReadError: chunk size 0 < 4
>>>
```

```python
>>> riff.RiffChunk.read(io.BytesIO(b'RIFF\x04\x00\x00\x00TE'))
Traceback (most recent call last):
  ...
riff.RiffChunkReadError: chunk format truncated
>>>
```