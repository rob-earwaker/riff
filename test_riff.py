import io
import unittest

import riff


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
