import io
import riff
import unittest


class TestCase(unittest.TestCase):
    def assertRaisesError(self, message):
        regex = '^{}$'.format(message)
        return self.assertRaisesRegex(riff.Error, regex)


class Test_Chunk_create(TestCase):
    def test_returns_Chunk_instance(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertIsInstance(chunk, riff.Chunk)

    def test_does_not_raise_with_empty_data_stream(self):
        datastream = io.BytesIO(b'')
        riff.Chunk.create('MOCK', 0, datastream)


class Test_Chunk_readfrom(TestCase):
    def test_returns_Chunk_instance(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(stream)
        self.assertIsInstance(chunk, riff.Chunk)

    def test_with_empty_chunk(self):
        stream = io.BytesIO(b'MOCK\x00\x00\x00\x00')
        riff.Chunk.readfrom(stream)

    def test_only_reads_header(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        riff.Chunk.readfrom(stream)
        self.assertEqual(8, stream.tell())

    def test_raises_when_id_truncated(self):
        stream = io.BytesIO(b'MOC')
        with self.assertRaisesError('chunk header truncated'):
            riff.Chunk.readfrom(stream)

    def test_raises_when_size_truncated(self):
        stream = io.BytesIO(b'MOCK\x08\x00')
        with self.assertRaisesError('chunk header truncated'):
            riff.Chunk.readfrom(stream)

    def test_raises_when_id_not_ascii(self):
        stream = io.BytesIO(b'M\xffCK\x08\x00\x00\x00MockData')
        with self.assertRaisesError('chunk id not ascii-decodable'):
            riff.Chunk.readfrom(stream)


class Test_Chunk_consumed(TestCase):
    def test_False_if_data_not_fully_consumed(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(stream)
        chunk.data.skip(4)
        self.assertFalse(chunk.consumed)

    def test_False_if_pad_expected_and_not_consumed(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.readfrom(stream)
        chunk.data.skipall()
        self.assertFalse(chunk.consumed)

    def test_False_if_pad_not_expected_and_not_consumed(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skipall()
        self.assertFalse(chunk.consumed)

    def test_True_if_no_data(self):
        stream = io.BytesIO(b'MOCK\x00\x00\x00\x00')
        chunk = riff.Chunk.readfrom(stream)
        self.assertTrue(chunk.consumed)

    def test_True_if_data_consumed_and_not_padded(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(stream)
        chunk.data.skipall()
        self.assertTrue(chunk.consumed)

    def test_True_if_data_consumed_and_pad_expected_and_read(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.readfrom(stream)
        chunk.data.skipall()
        chunk.readpad()
        self.assertTrue(chunk.consumed)

    def test_True_if_data_consumed_and_pad_not_expected_and_read(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skipall()
        chunk.readpad()
        self.assertTrue(chunk.consumed)

    def test_True_if_data_consumed_and_pad_expected_and_skipped(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.readfrom(stream)
        chunk.data.skipall()
        chunk.skippad()
        self.assertTrue(chunk.consumed)

    def test_True_if_data_consumed_and_pad_not_expected_and_skipped(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skipall()
        chunk.skippad()
        self.assertTrue(chunk.consumed)


class Test_Chunk_data(TestCase):
    def test_is_ChunkData_instance_after_creating_chunk(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertIsInstance(chunk.data, riff.ChunkData)

    def test_is_ChunkData_instance_after_reading_chunk_from_stream(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(stream)
        self.assertIsInstance(chunk.data, riff.ChunkData)


if __name__ == '__main__':
    unittest.main()
