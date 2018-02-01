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

## `riff.RiffChunk`

```python
>>> import io
>>> stream = io.BytesIO(b'RIFF\x04\x00\x00\x00TEST')
>>>
```

```python
>>> import riff
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