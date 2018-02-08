# [`riff.Chunk`](riff.Chunk.md#riffchunk)

A [`riff.Chunk`](riff.Chunk.md#riffchunk) instance represents a RIFF-formatted chunk, which consists of the following elements:

| Element    | # Bytes    | Format                                                      |
|------------|------------|-------------------------------------------------------------|
| Identifier | 4          | ASCII encoded string                                        |
| Size       | 4          | Little-endian unsigned integer                              |
| Data       | {size}     | Varies, multi-byte integers are assumed to be little-endian |
| Pad        | {size} % 2 | Any (only present if {size} is odd)                         |

A [`riff.Chunk`](riff.Chunk.md#riffchunk) instance can be created using one of the following class methods:

- [`riff.Chunk.create`](riff.Chunk.md#riffchunkcreate)
- [`riff.Chunk.readfrom`](riff.Chunk.md#riffchunkreadfrom)

Both of these methods return a [`riff.Chunk`](riff.Chunk.md#riffchunk) instance with the following attributes:

- [`{riff.Chunk}.consumed`](riff.Chunk.md#riffchunkconsumed)
- [`{riff.Chunk}.data`](riff.Chunk.md#riffchunkdata)
- [`{riff.Chunk}.id`](riff.Chunk.md#riffchunkid)
- [`{riff.Chunk}.padded`](riff.Chunk.md#riffchunkpadded)
- [`{riff.Chunk}.readover`](riff.Chunk.md#riffchunkreadover)
- [`{riff.Chunk}.readpad`](riff.Chunk.md#riffchunkreadpad)
- [`{riff.Chunk}.size`](riff.Chunk.md#riffchunksize)
- [`{riff.Chunk}.skip`](riff.Chunk.md#riffchunkskip)
- [`{riff.Chunk}.skippad`](riff.Chunk.md#riffchunkskippad)
- [`{riff.Chunk}.writeto`](riff.Chunk.md#riffchunkwriteto)


## [`riff.Chunk.create`](riff.Chunk.md#riffchunkcreate)

Not yet documented.


## [`riff.Chunk.readfrom`](riff.Chunk.md#riffchunkreadfrom)

Reads a [`riff.Chunk`](riff.Chunk.md#riffchunk) object from a binary I/O stream. The [`riff.Chunk.readfrom`](riff.Chunk.md#riffchunkreadfrom) method only reads the chunk's header (8 bytes) from the stream. 

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

The [`{riff.Chunk}.data`](riff.Chunk.md#riffchunkdata) property exposes the chunk's data, and the [`{riff.Chunk}.readpad`](riff.Chunk.md#riffchunkreadpad) method can be used to read the pad byte, if there is one. These attributes and the [`riff.Chunk.readfrom`](riff.Chunk.md#riffchunkreadfrom) method only use a single method on the input stream - `stream.read(size)`. This method is expected to return `size` bytes when called.

>IMPORTANT! While there is still unread chunk data (including the pad byte), the [`riff.Chunk`](riff.Chunk.md#riffchunk) object assumes the input stream is not being modified externally. Modifying the input stream before having read all of the 


## [`{riff.Chunk}.consumed`](riff.Chunk.md#riffchunkconsumed)

Not yet documented.


## [`{riff.Chunk}.data`](riff.Chunk.md#riffchunkdata)

The `data` property of a [`riff.Chunk`](riff.Chunk.md#riffchunk) object exposes the chunk's data as a stream-like [`riff.ChunkData`](riff.ChunkData.md#riffchunkdata) object, which has size equal to the chunk size.

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.data
riff.ChunkData(size=8)
>>>
```


## [`{riff.Chunk}.id`](riff.Chunk.md#riffchunkid)

The `id` property of a [`riff.Chunk`](riff.Chunk.md#riffchunk) object gives the 4-character ASCII string that identifies the chunk type.

```python
>>> stream = io.BytesIO(b'TEST\x08\x00\x00\x00TestData')
>>> chunk = riff.Chunk.read(stream)
>>> chunk.id
'TEST'
>>>
```


## [`{riff.Chunk}.padded`](riff.Chunk.md#riffchunkpadded)

Not yet documented.


## [`{riff.Chunk}.readover`](riff.Chunk.md#riffchunkreadover)

Not yet documented.


## [`{riff.Chunk}.readpad`](riff.Chunk.md#riffchunkreadpad)

Not yet documented.


## [`{riff.Chunk}.size`](riff.Chunk.md#riffchunksize)

The `size` property of a [`riff.Chunk`](riff.Chunk.md#riffchunk) object gives the number of bytes of data the chunk contains. This value does not include the 8 byte header, or the pad byte (if applicable).

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


## [`{riff.Chunk}.skip`](riff.Chunk.md#riffchunkskip)

Not yet documented.


## [`{riff.Chunk}.skippad`](riff.Chunk.md#riffchunkskippad)

Not yet documented.


## [`{riff.Chunk}.writeto`](riff.Chunk.md#riffchunkwriteto)

Not yet documented.
