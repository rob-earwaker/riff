# riff

```python
>>> import io
>>> stream = io.BytesIO(b'RIFF\x04\x00\x00\x00WAVE')
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
'WAVE'
>>>
```