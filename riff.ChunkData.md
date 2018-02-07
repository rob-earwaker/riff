# [`riff.ChunkData`](riff.ChunkData.md#riffchunkdata)

The [`riff.ChunkData`](riff.ChunkData.md#riffchunkdata) type provides a window over a section of the input stream object, where the window starts at the stream position corresponding to the start of the chunk's data and ends after the final byte of chunk data. Note that reading to the end of the chunk data will not necessarily correspond to the end of the input stream, but the [`riff.ChunkData`](riff.ChunkData.md#riffchunkdata) object will still behave as if it had reached the EOF.

A [`riff.ChunkData`](riff.ChunkData.md#riffchunkdata) object has the same interface as a read-only [`io.RawIOBase`](https://docs.python.org/library/io.html#io.RawIOBase) object. It will delegate to the corresponding methods on the input stream in most cases, with some additional constraints. The properties and methods that form the [`io.RawIOBase`](https://docs.python.org/library/io.html#io.RawIOBase) interface are listed below.

- [`<riff.ChunkData>.read`](riff.ChunkData.md#riffchunkdataread)
- [`<riff.ChunkData>.readall`](riff.ChunkData.md#riffchunkdatareadall)
- [`<riff.ChunkData>.seek`](riff.ChunkData.md#riffchunkdataseek)
- [`<riff.ChunkData>.seekable`](riff.ChunkData.md#riffchunkdataseekable)
- [`<riff.ChunkData>.tell`](riff.ChunkData.md#riffchunkdatatell)

As well as those defined by the [`io.RawIOBase`](https://docs.python.org/library/io.html#io.RawIOBase) interface, a [`riff.ChunkData`](riff.ChunkData.md#riffchunkdata) object defines the following additional properties and methods:

- [`<riff.ChunkData>.padded`](riff.ChunkData.md#riffchunkdatapadded)
- [`<riff.ChunkData>.size`](riff.ChunkData.md#riffchunkdatasize)
- [`<riff.ChunkData>.skip`](riff.ChunkData.md#riffchunkdataskip)


## [`<riff.ChunkData>.padded`](riff.ChunkData.md#riffchunkdatapadded)

The `padded` property of a [`riff.ChunkData`](riff.ChunkData.md#riffchunkdata) object indicates whether the chunk requires a pad byte at the end of the data block. This will be `True` if the chunk size is odd, and `False` if the chunk size is even.

```python
>>> import io
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>> import riff
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.padded
False
>>>
>>> stream = io.BytesIO(b'TEST\x07\x00\x00\x00OddData\x00')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.padded
True
>>>
```


## [`<riff.ChunkData>.read`](riff.ChunkData.md#riffchunkdataread)

Not yet documented.


## [`<riff.ChunkData>.readall`](riff.ChunkData.md#riffchunkdatareadall)

Not yet documented.


## [`<riff.ChunkData>.seek`](riff.ChunkData.md#riffchunkdataseek)

Not yet documented.


## [`<riff.ChunkData>.seekable`](riff.ChunkData.md#riffchunkdataseekable)

The `seekable` method of a [`riff.ChunkData`](riff.ChunkData.md#riffchunkdata) object delegates to the corresponding method of the input stream.

```python
>>> import io
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>> import riff
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.seekable()
True
>>>
```


## [`<riff.ChunkData>.size`](riff.ChunkData.md#riffchunkdatasize)

The `size` property of a [`riff.ChunkData`](riff.ChunkData.md#riffchunkdata) object gives the size in bytes of the data stream. Unlike in a typical IO stream, the size is known because it is provided by the chunk's header. Note that the size does not include the pad byte (if applicable).

```python
>>> import io
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>> import riff
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.size
8
>>>
>>> stream = io.BytesIO(b'TEST\x07\x00\x00\x00OddData\x00')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.size
7
>>>
```


## [`<riff.ChunkData>.skip`](riff.ChunkData.md#riffchunkdataskip)

The `skip` method of a [`riff.ChunkData`](riff.ChunkData.md#riffchunkdata) object moves the cursor to the end of the chunk data stream.

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestDataExtraData')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.skip()
>>> stream.read(9)
b'ExtraData'
>>>
```

Data is skipped from the current position within the chunk data, so will work after reading all or part of the chunk's data.

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

For non-seekable input streams this method will raise an [`OSError`](https://docs.python.org/library/exceptions.html#OSError).

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>> stream.seekable = lambda: False
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.skip()
Traceback (most recent call last):
  ...
OSError: chunk data is not seekable
>>>
```


## [`<riff.ChunkData>.tell`](riff.ChunkData.md#riffchunkdatatell)

The `tell` method of a [`riff.ChunkData`](riff.ChunkData.md#riffchunkdata) object gives the position of the cursor within the chunk, relative to the start of the data.

```python
>>> import io
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>> import riff
>>> chunk = riff.Chunk.read(stream)
>>> stream.tell()
8
>>> chunk.data.tell()
0
>>> chunk.data.read(4)
b'Test'
>>> chunk.data.tell()
4
>>>
```

Unlike most non-seekable streams, the [`<riff.ChunkData>.tell`](riff.ChunkData.md#riffchunkdatatell) method will not raise an exception if the stream is not seekable.

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>> stream.seekable = lambda: False
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data.tell()
0
>>>
```
