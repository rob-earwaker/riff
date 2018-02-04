# `riff.RiffChunk`

```python
>>> import io
>>> stream = io.BytesIO(b'RIFF\x04\x00\x00\x00TEST')
>>>
>>> import riff
>>> riff.RiffChunk.read(stream)
riff.RiffChunk(size=4, format='TEST')
>>> stream.tell()
12
>>>
```

## Exceptions

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
