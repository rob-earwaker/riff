import io
import unittest

import riff


class TestStream(unittest.TestCase):
    def test__from_stream__when_base_stream_is_stream_instance(self):
        base_stream = riff.Stream.from_stream(io.BytesIO(b'MOCK'))
        stream = riff.Stream.from_stream(base_stream)
        self.assertIs(base_stream, stream)

    def test__tell__when_init_with_base_stream_pointer_at_start(self):
        base_stream = io.BytesIO(b'MOCK')
        stream = riff.Stream.from_stream(base_stream)
        self.assertEqual(0, stream.tell())

    def test__tell__when_init_with_base_stream_pointer_in_middle(self):
        base_stream = io.BytesIO(b'MOCK')
        base_stream.seek(3)
        stream = riff.Stream.from_stream(base_stream)
        self.assertEqual(3, stream.tell())

    def test__tell__when_init_with_base_stream_pointer_after_end(self):
        base_stream = io.BytesIO(b'MOCK')
        base_stream.seek(7)
        stream = riff.Stream.from_stream(base_stream)
        self.assertEqual(7, stream.tell())

    def test__tell__after_base_stream_seek_to_start(self):
        base_stream = io.BytesIO(b'MOCK')
        base_stream.seek(1)
        stream = riff.Stream.from_stream(base_stream)
        base_stream.seek(0)
        self.assertEqual(0, stream.tell())

    def test__tell__after_base_stream_seek_to_middle(self):
        base_stream = io.BytesIO(b'MOCK')
        stream = riff.Stream.from_stream(base_stream)
        base_stream.seek(2)
        self.assertEqual(2, stream.tell())

    def test__tell__after_base_stream_seek_after_end(self):
        base_stream = io.BytesIO(b'MOCK')
        stream = riff.Stream.from_stream(base_stream)
        base_stream.seek(9)
        self.assertEqual(9, stream.tell())

    def test__tell__after_read_to_middle(self):
        base_stream = io.BytesIO(b'MOCK')
        stream = riff.Stream.from_stream(base_stream)
        stream.read(2)
        self.assertEqual(2, stream.tell())

    def test__tell__after_read_past_end(self):
        base_stream = io.BytesIO(b'MOCK')
        stream = riff.Stream.from_stream(base_stream)
        base_stream.read(7)
        self.assertEqual(4, stream.tell())


class TestRiffChunk(unittest.TestCase):
    def test_chunk_id(self):
        self.assertEqual('RIFF', riff.RiffChunk.ID)

    def test_read_from_stream_with_invalid_chunk_id(self):
        stream = io.BytesIO(b'MOCK\x04\x00\x00\x00LIST')
        with self.assertRaises(riff.ChunkIdInvalid) as context:
            riff.RiffChunk.from_stream(stream)
        self.assertEqual('MOCK != RIFF', str(context.exception))

    def test_read_chunk_id_from_stream(self):
        stream = io.BytesIO(b'RIFF\x04\x00\x00\x00MOCK')
        riff_chunk = riff.RiffChunk.from_stream(stream)
        self.assertEqual('RIFF', riff_chunk.id)

    def test_read_chunk_size_from_stream(self):
        stream = io.BytesIO(b'RIFF\x04\x00\x00\x00MOCK')
        riff_chunk = riff.RiffChunk.from_stream(stream)
        self.assertEqual(4, riff_chunk.size)

    def test_read_riff_format_from_stream(self):
        stream = io.BytesIO(b'RIFF\x04\x00\x00\x00MOCK')
        riff_chunk = riff.RiffChunk.from_stream(stream)
        self.assertEqual('MOCK', riff_chunk.format)

    def test_read_subchunks_from_stream(self):
        stream = io.BytesIO(
            b'RIFF\x20\x00\x00\x00MOCK' +
            b'CK01\x04\x00\x00\x001111' +
            b'CK02\x08\x00\x00\x0022222222'
        )
        riff_chunk = riff.RiffChunk.from_stream(stream)
        self.assertEqual('CK01', riff_chunk.subchunk(0).id)
        self.assertEqual(4, riff_chunk.subchunk(0).size)
        self.assertEqual(b'1111', riff_chunk.subchunk(0).data)
        self.assertEqual('CK02', riff_chunk.subchunk(1).id)
        self.assertEqual(8, riff_chunk.subchunk(1).size)
        self.assertEqual(b'22222222', riff_chunk.subchunk(1).data)

    def test_read_from_stream_with_truncated_chunk_id(self):
        stream = io.BytesIO(b'RIF')
        with self.assertRaises(riff.UnexpectedEndOfStream) as context:
            riff.RiffChunk.from_stream(stream)
        self.assertEqual(
            'Expected 1 more byte(s) after position 3', str(context.exception)
        )

    def test_read_from_stream_with_truncated_chunk_size(self):
        stream = io.BytesIO(b'RIFF\x04\x00')
        with self.assertRaises(riff.UnexpectedEndOfStream) as context:
            riff.RiffChunk.from_stream(stream)
        self.assertEqual(
            'Expected 2 more byte(s) after position 6', str(context.exception)
        )

    def test_read_from_stream_with_truncated_riff_data(self):
        stream = io.BytesIO(b'RIFF\x08\x00\x00\x00MOCKDAT')
        with self.assertRaises(riff.UnexpectedEndOfStream) as context:
            riff.RiffChunk.from_stream(stream)
        self.assertEqual(
            'Expected 1 more byte(s) after position 15', str(context.exception)
        )


if __name__ == '__main__':
    unittest.main()
