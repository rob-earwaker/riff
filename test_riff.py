import io
import riff
import unittest


class TestChunk(unittest.TestCase):
    def test_readfrom_only_reads_header(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        riff.Chunk.readfrom(stream)
        self.assertEqual(8, stream.tell())


if __name__ == '__main__':
    unittest.main()
