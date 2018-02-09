import io
import riff
import unittest
import unittest.mock


class TestCase(unittest.TestCase):
    def assertRaisesError(self, message):
        regex = '^{}$'.format(message)
        return self.assertRaisesRegex(riff.Error, regex)


class Test_Chunk_create(TestCase):
    def test_returns_Chunk_instance(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertIsInstance(chunk, riff.Chunk)

    def test_no_error_with_empty_data_stream(self):
        datastream = io.BytesIO(b'')
        riff.Chunk.create('MOCK', 0, datastream)

    def test_does_not_read_data_stream(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertEqual(0, datastream.tell())


class Test_Chunk_readfrom(TestCase):
    def test_returns_Chunk_instance(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(stream)
        self.assertIsInstance(chunk, riff.Chunk)

    def test_no_error_with_empty_chunk(self):
        stream = io.BytesIO(b'MOCK\x00\x00\x00\x00')
        riff.Chunk.readfrom(stream)

    def test_only_reads_header(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        riff.Chunk.readfrom(stream)
        self.assertEqual(8, stream.tell())

    def test_error_when_id_truncated(self):
        stream = io.BytesIO(b'MOC')
        with self.assertRaisesError('chunk header truncated'):
            riff.Chunk.readfrom(stream)

    def test_error_when_size_truncated(self):
        stream = io.BytesIO(b'MOCK\x08\x00')
        with self.assertRaisesError('chunk header truncated'):
            riff.Chunk.readfrom(stream)

    def test_error_when_id_not_ascii(self):
        stream = io.BytesIO(b'M\xffCK\x08\x00\x00\x00MockData')
        with self.assertRaisesError('chunk id not ascii-decodable'):
            riff.Chunk.readfrom(stream)


class Test_Chunk_consumed(TestCase):
    def test_False_if_data_not_fully_consumed(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(stream)
        chunk.data.skip(4)
        self.assertFalse(chunk.consumed)

    def test_False_if_pad_byte_expected_and_not_consumed(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.readfrom(stream)
        chunk.data.skipall()
        self.assertFalse(chunk.consumed)

    def test_False_if_pad_byte_not_expected_and_not_consumed(self):
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

    def test_True_if_data_consumed_and_pad_byte_expected_and_read(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.readfrom(stream)
        chunk.data.skipall()
        chunk.readpadbyte()
        self.assertTrue(chunk.consumed)

    def test_True_if_data_consumed_and_pad_byte_not_expected_and_read(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skipall()
        chunk.readpadbyte()
        self.assertTrue(chunk.consumed)

    def test_True_if_data_consumed_and_pad_byte_expected_and_skipped(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.readfrom(stream)
        chunk.data.skipall()
        chunk.skippadbyte()
        self.assertTrue(chunk.consumed)

    def test_True_if_data_consumed_and_pad_byte_not_expected_and_skipped(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skipall()
        chunk.skippadbyte()
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


class Test_Chunk_id(TestCase):
    def test_value_after_creating_chunk(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertEqual('MOCK', chunk.id)

    def test_value_after_reading_chunk_from_stream(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(stream)
        self.assertEqual('MOCK', chunk.id)


class Test_Chunk_padded(TestCase):
    def test_True_if_size_odd_and_pad_byte_expected(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.readfrom(stream)
        self.assertTrue(chunk.padded)

    def test_True_if_size_odd_and_pad_byte_not_expected(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        self.assertTrue(chunk.padded)

    def test_False_if_size_even_and_pad_byte_expected(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(stream)
        self.assertFalse(chunk.padded)

    def test_False_if_size_even_and_pad_byte_not_expected(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertFalse(chunk.padded)


class Test_Chunk_readover(TestCase):
    def test_consumes_chunk_when_not_padded_and_pad_byte_expected(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(stream)
        chunk.readover()
        self.assertTrue(chunk.consumed)

    def test_consumes_chunk_when_padded_and_pad_byte_expected(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.readfrom(stream)
        chunk.readover()
        self.assertTrue(chunk.consumed)

    def test_consumes_chunk_when_not_padded_and_pad_byte_not_expected(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        chunk.readover()
        self.assertTrue(chunk.consumed)

    def test_consumes_chunk_when_padded_and_pad_byte_not_expected(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.readover()
        self.assertTrue(chunk.consumed)

    def test_does_not_read_more_than_buffer_size_bytes_at_once(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.readfrom(stream)
        stream.read = unittest.mock.Mock()
        stream.read.side_effect = lambda size: b'\x00' * size
        chunk.readover(buffersize=4)
        read_sizes = [args[0] for args, _ in stream.read.call_args_list]
        self.assertTrue(all(size <= 4 for size in read_sizes))


class Test_Chunk_readpadbyte(TestCase):
    def test_error_if_chunk_data_not_consumed(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(stream)
        chunk.data.skip(4)
        with self.assertRaisesError('not all chunk data has been consumed'):
            chunk.readpadbyte()

    def test_no_pad_byte_if_not_padded(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(stream)
        chunk.data.skipall()
        padbyte = chunk.readpadbyte()
        self.assertEqual(b'', padbyte)

    def test_no_pad_byte_if_pad_already_read(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.readfrom(stream)
        chunk.data.skipall()
        chunk.readpadbyte()
        padbyte = chunk.readpadbyte()
        self.assertEqual(b'', padbyte)

    def test_no_pad_byte_if_pad_already_skipped(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.readfrom(stream)
        chunk.data.skipall()
        chunk.skippadbyte()
        padbyte = chunk.readpadbyte()
        self.assertEqual(b'', padbyte)

    def test_zero_pad_byte_if_pad_byte_not_expected(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skipall()
        padbyte = chunk.readpadbyte()
        self.assertEqual(b'\x00', padbyte)

    def test_error_if_pad_byte_expected_but_not_present(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd')
        chunk = riff.Chunk.readfrom(stream)
        chunk.data.skipall()
        with self.assertRaisesError('chunk truncated - expected pad byte'):
            chunk.readpadbyte()

    def test_reads_pad_byte_if_pad_byte_expected(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x77')
        chunk = riff.Chunk.readfrom(stream)
        chunk.data.skipall()
        padbyte = chunk.readpadbyte()
        self.assertEqual(b'\x77', padbyte)


if __name__ == '__main__':
    unittest.main()
