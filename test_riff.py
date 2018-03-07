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
        riff.Chunk.create('MOCK', 8, datastream)
        self.assertEqual(0, datastream.tell())


class Test_Chunk_streamfrom(TestCase):
    def test_returns_Chunk_instance(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertIsInstance(chunk, riff.Chunk)

    def test_no_error_with_empty_chunk(self):
        stream = io.BytesIO(b'MOCK\x00\x00\x00\x00')
        riff.Chunk.streamfrom(stream)

    def test_only_reads_header(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        riff.Chunk.streamfrom(stream)
        self.assertEqual(8, stream.tell())

    def test_error_when_id_truncated(self):
        stream = io.BytesIO(b'MOC')
        with self.assertRaisesError('chunk header truncated'):
            riff.Chunk.streamfrom(stream)

    def test_error_when_size_truncated(self):
        stream = io.BytesIO(b'MOCK\x08\x00')
        with self.assertRaisesError('chunk header truncated'):
            riff.Chunk.streamfrom(stream)

    def test_error_when_id_not_ascii(self):
        stream = io.BytesIO(b'M\xffCK\x08\x00\x00\x00MockData')
        with self.assertRaisesError('chunk id not ascii-decodable'):
            riff.Chunk.streamfrom(stream)


class Test_Chunk_consumed(TestCase):
    def test_False_if_data_not_fully_consumed(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skip(4)
        self.assertFalse(chunk.consumed)

    def test_False_if_pad_byte_expected_and_not_consumed(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skipall()
        self.assertFalse(chunk.consumed)

    def test_False_if_pad_byte_not_expected_and_not_consumed(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skipall()
        self.assertFalse(chunk.consumed)

    def test_True_if_no_data(self):
        stream = io.BytesIO(b'MOCK\x00\x00\x00\x00')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertTrue(chunk.consumed)

    def test_True_if_data_consumed_and_not_padded(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skipall()
        self.assertTrue(chunk.consumed)

    def test_True_if_data_consumed_and_pad_byte_expected_and_read(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
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
        chunk = riff.Chunk.streamfrom(stream)
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
        chunk = riff.Chunk.streamfrom(stream)
        self.assertIsInstance(chunk.data, riff.ChunkData)


class Test_Chunk_id(TestCase):
    def test_value_after_creating_chunk(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertEqual('MOCK', chunk.id)

    def test_value_after_reading_chunk_from_stream(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertEqual('MOCK', chunk.id)


class Test_Chunk_padded(TestCase):
    def test_True_if_size_odd_and_pad_byte_expected(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertTrue(chunk.padded)

    def test_True_if_size_odd_and_pad_byte_not_expected(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        self.assertTrue(chunk.padded)

    def test_False_if_size_even_and_pad_byte_expected(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertFalse(chunk.padded)

    def test_False_if_size_even_and_pad_byte_not_expected(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertFalse(chunk.padded)


class Test_Chunk_size(TestCase):
    def test_value_after_creating_unpadded_chunk(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertEqual(8, chunk.size)

    def test_value_after_reading_unpadded_chunk_from_stream(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertEqual(8, chunk.size)

    def test_value_after_creating_padded_chunk(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        self.assertEqual(11, chunk.size)

    def test_value_after_reading_padded_chunk_from_stream(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertEqual(11, chunk.size)


class Test_Chunk_totalsize(TestCase):
    def test_with_unpadded_chunk_read_from_stream(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertEqual(16, chunk.totalsize)

    def test_with_padded_chunk_read_from_stream(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertEqual(20, chunk.totalsize)

    def test_with_unpadded_created_chunk(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertEqual(16, chunk.totalsize)

    def test_with_padded_created_chunk(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        self.assertEqual(20, chunk.totalsize)


class Test_Chunk_readover(TestCase):
    def test_consumes_chunk_when_not_padded_and_pad_byte_expected(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.readover()
        self.assertTrue(chunk.consumed)

    def test_consumes_chunk_when_padded_and_pad_byte_expected(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
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
        chunk = riff.Chunk.streamfrom(stream)
        stream.read = unittest.mock.Mock()
        stream.read.side_effect = lambda size: b'\x00' * size
        chunk.readover(buffersize=4)
        read_sizes = [args[0] for args, _ in stream.read.call_args_list]
        self.assertTrue(all(size <= 4 for size in read_sizes))


class Test_Chunk_readpadbyte(TestCase):
    def test_error_if_chunk_data_not_consumed(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skip(4)
        with self.assertRaisesError('not all chunk data has been consumed'):
            chunk.readpadbyte()

    def test_no_pad_byte_if_not_padded(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skipall()
        padbyte = chunk.readpadbyte()
        self.assertEqual(b'', padbyte)

    def test_no_pad_byte_if_pad_byte_already_read(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skipall()
        chunk.readpadbyte()
        padbyte = chunk.readpadbyte()
        self.assertEqual(b'', padbyte)

    def test_no_pad_byte_if_pad_byte_already_skipped(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
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
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skipall()
        with self.assertRaisesError('chunk truncated - expected pad byte'):
            chunk.readpadbyte()

    def test_reads_pad_byte_if_pad_byte_expected(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x77')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skipall()
        padbyte = chunk.readpadbyte()
        self.assertEqual(b'\x77', padbyte)


class Test_Chunk_skip(TestCase):
    def test_consumes_chunk_when_not_padded_and_pad_byte_expected(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.skip()
        self.assertTrue(chunk.consumed)

    def test_consumes_chunk_when_padded_and_pad_byte_expected(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.skip()
        self.assertTrue(chunk.consumed)

    def test_consumes_chunk_when_not_padded_and_pad_byte_not_expected(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        chunk.skip()
        self.assertTrue(chunk.consumed)

    def test_consumes_chunk_when_padded_and_pad_byte_not_expected(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.skip()
        self.assertTrue(chunk.consumed)

    def test_error_if_stream_has_no_seek_method(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        stream.seek = unittest.mock.Mock(side_effect=AttributeError)
        chunk = riff.Chunk.streamfrom(stream)
        with self.assertRaisesError('stream is not seekable'):
            chunk.skip()

    def test_error_if_stream_not_seekable(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        stream.seek = unittest.mock.Mock(side_effect=OSError)
        chunk = riff.Chunk.streamfrom(stream)
        with self.assertRaisesError('stream is not seekable'):
            chunk.skip()

    def test_does_not_read_from_stream(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        stream.read = unittest.mock.Mock()
        stream.read.side_effect = lambda size: b'\x00' * size
        chunk.skip()
        stream.read.assert_not_called()


class Test_Chunk_skippadbyte(TestCase):
    def test_error_if_chunk_data_not_consumed(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skip(4)
        with self.assertRaisesError('not all chunk data has been consumed'):
            chunk.skippadbyte()

    def test_stream_position_unchanged_if_not_padded(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skipall()
        position_before = stream.tell()
        chunk.skippadbyte()
        self.assertEqual(position_before, stream.tell())

    def test_stream_position_unchanged_if_pad_byte_already_read(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skipall()
        chunk.readpadbyte()
        position_before = stream.tell()
        chunk.skippadbyte()
        self.assertEqual(position_before, stream.tell())

    def test_stream_position_unchanged_if_pad_byte_already_skipped(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skipall()
        chunk.skippadbyte()
        position_before = stream.tell()
        chunk.skippadbyte()
        self.assertEqual(position_before, stream.tell())

    def test_stream_position_unchanged_if_pad_byte_not_expected(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skipall()
        position_before = datastream.tell()
        chunk.skippadbyte()
        self.assertEqual(position_before, datastream.tell())

    def test_stream_position_advanced_if_pad_byte_expected(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skipall()
        position_before = stream.tell()
        chunk.skippadbyte()
        self.assertEqual(position_before + 1, stream.tell())

    def test_error_if_stream_has_no_seek_method(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skipall()
        stream.seek = unittest.mock.Mock(side_effect=AttributeError)
        with self.assertRaisesError('stream is not seekable'):
            chunk.skippadbyte()

    def test_error_if_stream_not_seekable(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skipall()
        stream.seek = unittest.mock.Mock(side_effect=OSError)
        with self.assertRaisesError('stream is not seekable'):
            chunk.skippadbyte()


class Test_Chunk_writeto(TestCase):
    def test_error_if_chunk_data_partially_consumed(self):
        instream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(instream)
        chunk.data.skip(4)
        outstream = io.BytesIO()
        with self.assertRaisesError('chunk partially consumed'):
            chunk.writeto(outstream)

    def test_read_then_write_preserves_bytes(self):
        instream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x77')
        chunk = riff.Chunk.streamfrom(instream)
        outstream = io.BytesIO()
        chunk.writeto(outstream)
        self.assertEqual(instream.getvalue(), outstream.getvalue())

    def test_writes_created_unpadded_chunk(self):
        datastream = io.BytesIO(b'Data')
        chunk = riff.Chunk.create('MOCK', 4, datastream)
        outstream = io.BytesIO()
        chunk.writeto(outstream)
        self.assertEqual(b'MOCK\x04\x00\x00\x00Data', outstream.getvalue())

    def test_writes_zero_pad_byte_for_created_padded_chunk(self):
        datastream = io.BytesIO(b'Odd')
        chunk = riff.Chunk.create('MOCK', 3, datastream)
        outstream = io.BytesIO()
        chunk.writeto(outstream)
        self.assertEqual(b'MOCK\x03\x00\x00\x00Odd\x00', outstream.getvalue())

    def test_does_not_read_more_than_buffer_size_bytes_at_once(self):
        instream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(instream)
        instream.read = unittest.mock.Mock()
        instream.read.side_effect = lambda size: b'\x00' * size
        outstream = io.BytesIO()
        chunk.writeto(outstream, buffersize=4)
        read_sizes = [args[0] for args, _ in instream.read.call_args_list]
        self.assertTrue(all(size <= 4 for size in read_sizes))


class Test_Chunk_repr(TestCase):
    def test_for_unpadded_chunk_read_from_stream(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertEqual("riff.Chunk(id='MOCK', size=8)", repr(chunk))

    def test_for_padded_chunk_read_from_stream(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertEqual("riff.Chunk(id='MOCK', size=11)", repr(chunk))

    def test_for_unpadded_created_chunk(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertEqual("riff.Chunk(id='MOCK', size=8)", repr(chunk))

    def test_for_padded_created_chunk(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        self.assertEqual("riff.Chunk(id='MOCK', size=11)", repr(chunk))


class Test_ChunkData_consumed(TestCase):
    def test_False_if_data_not_fully_consumed(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        chunk.data.skip(4)
        self.assertFalse(chunk.data.consumed)

    def test_True_if_all_data_read(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        chunk.data.read(8)
        self.assertTrue(chunk.data.consumed)

    def test_True_if_all_data_skipped(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        chunk.data.skip(8)
        self.assertTrue(chunk.data.consumed)


class Test_ChunkData_position(TestCase):
    def test_intially_zero_when_chunk_created(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertEqual(0, chunk.data.position)

    def test_intially_zero_when_chunk_read_from_stream(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertEqual(0, chunk.data.position)

    def test_advances_by_size_when_reading(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        chunk.data.read(4)
        self.assertEqual(4, chunk.data.position)

    def test_advances_by_size_when_skipping(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        chunk.data.skip(4)
        self.assertEqual(4, chunk.data.position)

    def test_does_not_exceed_size_when_reading_too_many_bytes(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.read(12)
        self.assertEqual(11, chunk.data.position)

    def test_does_not_exceed_size_when_skipping_too_many_bytes(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skip(12)
        self.assertEqual(11, chunk.data.position)


class Test_ChunkData_size(TestCase):
    def test_for_unpadded_chunk_read_from_stream(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertEqual(8, chunk.data.size)

    def test_for_padded_chunk_read_from_stream(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertEqual(11, chunk.data.size)

    def test_for_unpadded_created_chunk(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertEqual(8, chunk.data.size)

    def test_for_padded_created_chunk(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        self.assertEqual(11, chunk.data.size)


class Test_ChunkData_read(TestCase):
    def test_buffer_empty_for_negative_size(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        buffer = chunk.data.read(-1)
        self.assertEqual(b'', buffer)

    def test_buffer_empty_for_zero_size(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        buffer = chunk.data.read(0)
        self.assertEqual(b'', buffer)

    def test_buffer_empty_if_all_data_already_read(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.read(11)
        buffer = chunk.data.read(1)
        self.assertEqual(b'', buffer)

    def test_buffer_empty_if_all_data_already_skipped(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skip(11)
        buffer = chunk.data.read(1)
        self.assertEqual(b'', buffer)

    def test_position_not_advanced_for_negative_size(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        position_before = chunk.data.position
        chunk.data.read(-1)
        self.assertEqual(position_before, chunk.data.position)

    def test_position_not_advanced_for_zero_size(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        position_before = chunk.data.position
        chunk.data.read(0)
        self.assertEqual(position_before, chunk.data.position)

    def test_position_not_advanced_if_all_data_already_read(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.read(11)
        position_before = chunk.data.position
        chunk.data.read(1)
        self.assertEqual(position_before, chunk.data.position)

    def test_position_not_advanced_if_all_data_already_skipped(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skip(11)
        position_before = chunk.data.position
        chunk.data.read(1)
        self.assertEqual(position_before, chunk.data.position)

    def test_stream_not_read_for_negative_size(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        stream.read = unittest.mock.Mock()
        stream.read.side_effect = lambda size: b'\x00' * size
        chunk.data.read(-1)
        stream.read.assert_not_called()

    def test_stream_not_read_for_zero_size(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        stream.read = unittest.mock.Mock()
        stream.read.side_effect = lambda size: b'\x00' * size
        chunk.data.read(0)
        stream.read.assert_not_called()

    def test_stream_not_read_if_all_data_already_read(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.read(11)
        stream.read = unittest.mock.Mock()
        stream.read.side_effect = lambda size: b'\x00' * size
        chunk.data.read(1)
        stream.read.assert_not_called()

    def test_stream_not_read_if_all_data_already_skipped(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skip(11)
        stream.read = unittest.mock.Mock()
        stream.read.side_effect = lambda size: b'\x00' * size
        chunk.data.read(1)
        stream.read.assert_not_called()

    def test_error_if_chunk_data_truncated(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00Mock')
        chunk = riff.Chunk.streamfrom(stream)
        with self.assertRaisesError('chunk data truncated'):
            chunk.data.read(5)

    def test_position_advanced_despite_truncation_error(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00Mock')
        chunk = riff.Chunk.streamfrom(stream)
        try:
            chunk.data.read(5)
        except riff.Error:
            pass
        self.assertEqual(4, chunk.data.position)

    def test_buffer_size_bytes_returned(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        buffer = chunk.data.read(4)
        self.assertEqual(b'Mock', buffer)

    def test_cannot_read_more_than_size_bytes(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        buffer = chunk.data.read(12)
        self.assertEqual(11, len(buffer))

    def test_cannot_read_more_than_size_bytes_in_total(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.read(4)
        buffer = chunk.data.read(8)
        self.assertEqual(7, len(buffer))

    def test_stream_position_not_advanced_more_than_size_bytes(self):
        datastream = io.BytesIO(b'MockDataOdd\x00')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.read(12)
        self.assertEqual(11, datastream.tell())

    def test_stream_position_not_advanced_more_than_size_bytes_in_total(self):
        datastream = io.BytesIO(b'MockDataOdd\x00')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.read(4)
        chunk.data.read(8)
        self.assertEqual(11, datastream.tell())


class Test_ChunkData_readall(TestCase):
    def test_reads_all_bytes_from_start(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        buffer = chunk.data.readall()
        self.assertEqual(b'MockDataOdd', buffer)

    def test_reads_all_bytes_from_position(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skip(4)
        buffer = chunk.data.readall()
        self.assertEqual(b'DataOdd', buffer)

    def test_consumes_chunk_data(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.readall()
        self.assertTrue(chunk.data.consumed)

    def test_error_if_chunk_data_truncated(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00Mock')
        chunk = riff.Chunk.streamfrom(stream)
        with self.assertRaisesError('chunk data truncated'):
            chunk.data.readall()

    def test_position_advanced_despite_truncation_error(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00Mock')
        chunk = riff.Chunk.streamfrom(stream)
        try:
            chunk.data.readall()
        except riff.Error:
            pass
        self.assertEqual(4, chunk.data.position)


class Test_ChunkData_readover(TestCase):
    def test_position_not_advanced_for_negative_size(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        position_before = chunk.data.position
        chunk.data.readover(-1)
        self.assertEqual(position_before, chunk.data.position)

    def test_position_not_advanced_for_zero_size(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        position_before = chunk.data.position
        chunk.data.readover(0)
        self.assertEqual(position_before, chunk.data.position)

    def test_position_not_advanced_if_all_data_already_read(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.read(11)
        position_before = chunk.data.position
        chunk.data.readover(1)
        self.assertEqual(position_before, chunk.data.position)

    def test_position_not_advanced_if_all_data_already_skipped(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skip(11)
        position_before = chunk.data.position
        chunk.data.readover(1)
        self.assertEqual(position_before, chunk.data.position)

    def test_stream_not_read_for_negative_size(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        stream.read = unittest.mock.Mock()
        stream.read.side_effect = lambda size: b'\x00' * size
        chunk.data.readover(-1)
        stream.read.assert_not_called()

    def test_stream_not_read_for_zero_size(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        stream.read = unittest.mock.Mock()
        stream.read.side_effect = lambda size: b'\x00' * size
        chunk.data.readover(0)
        stream.read.assert_not_called()

    def test_stream_not_read_if_all_data_already_read(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.read(11)
        stream.read = unittest.mock.Mock()
        stream.read.side_effect = lambda size: b'\x00' * size
        chunk.data.readover(1)
        stream.read.assert_not_called()

    def test_stream_not_read_if_all_data_already_skipped(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skip(11)
        stream.read = unittest.mock.Mock()
        stream.read.side_effect = lambda size: b'\x00' * size
        chunk.data.readover(1)
        stream.read.assert_not_called()

    def test_error_if_chunk_data_truncated(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00Mock')
        chunk = riff.Chunk.streamfrom(stream)
        with self.assertRaisesError('chunk data truncated'):
            chunk.data.readover(5)

    def test_position_advanced_despite_truncation_error(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00Mock')
        chunk = riff.Chunk.streamfrom(stream)
        try:
            chunk.data.readover(5)
        except riff.Error:
            pass
        self.assertEqual(4, chunk.data.position)

    def test_stream_position_not_advanced_more_than_size_bytes(self):
        datastream = io.BytesIO(b'MockDataOdd\x00')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.readover(12)
        self.assertEqual(11, datastream.tell())

    def test_stream_position_not_advanced_more_than_size_bytes_in_total(self):
        datastream = io.BytesIO(b'MockDataOdd\x00')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.readover(4)
        chunk.data.readover(8)
        self.assertEqual(11, datastream.tell())

    def test_does_not_read_more_than_buffer_size_bytes_at_once(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        stream.read = unittest.mock.Mock()
        stream.read.side_effect = lambda size: b'\x00' * size
        chunk.data.readover(11, buffersize=4)
        read_sizes = [args[0] for args, _ in stream.read.call_args_list]
        self.assertTrue(all(size <= 4 for size in read_sizes))


class Test_ChunkData_readoverall(TestCase):
    def test_advances_position_to_end_from_start(self):
        datastream = io.BytesIO(b'MockDataOdd\x00')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.readoverall()
        self.assertEqual(11, chunk.data.position)

    def test_advances_position_to_end_from_current_position(self):
        datastream = io.BytesIO(b'MockDataOdd\x00')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skip(4)
        chunk.data.readoverall()
        self.assertEqual(11, chunk.data.position)

    def test_consumes_chunk_data(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.readoverall()
        self.assertTrue(chunk.data.consumed)

    def test_does_not_read_more_than_buffer_size_bytes_at_once(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        stream.read = unittest.mock.Mock()
        stream.read.side_effect = lambda size: b'\x00' * size
        chunk.data.readoverall(buffersize=4)
        read_sizes = [args[0] for args, _ in stream.read.call_args_list]
        self.assertTrue(all(size <= 4 for size in read_sizes))

    def test_error_if_chunk_data_truncated(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00Mock')
        chunk = riff.Chunk.streamfrom(stream)
        with self.assertRaisesError('chunk data truncated'):
            chunk.data.readoverall()

    def test_position_advanced_despite_truncation_error(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00Mock')
        chunk = riff.Chunk.streamfrom(stream)
        try:
            chunk.data.readoverall()
        except riff.Error:
            pass
        self.assertEqual(4, chunk.data.position)


class Test_ChunkData_skip(TestCase):
    def test_position_not_advanced_for_negative_size(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        position_before = chunk.data.position
        chunk.data.skip(-1)
        self.assertEqual(position_before, chunk.data.position)

    def test_position_not_advanced_for_zero_size(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        position_before = chunk.data.position
        chunk.data.skip(0)
        self.assertEqual(position_before, chunk.data.position)

    def test_position_not_advanced_if_all_data_already_read(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.read(11)
        position_before = chunk.data.position
        chunk.data.skip(1)
        self.assertEqual(position_before, chunk.data.position)

    def test_position_not_advanced_if_all_data_already_skipped(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skip(11)
        position_before = chunk.data.position
        chunk.data.skip(1)
        self.assertEqual(position_before, chunk.data.position)

    def test_stream_not_seeked_for_negative_size(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        stream.seek = unittest.mock.Mock()
        chunk.data.skip(-1)
        stream.seek.assert_not_called()

    def test_stream_not_seeked_for_zero_size(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        stream.seek = unittest.mock.Mock()
        chunk.data.skip(0)
        stream.seek.assert_not_called()

    def test_stream_not_seeked_if_all_data_already_read(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.read(11)
        stream.seek = unittest.mock.Mock()
        chunk.data.skip(1)
        stream.seek.assert_not_called()

    def test_stream_not_seeked_if_all_data_already_skipped(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skip(11)
        stream.seek = unittest.mock.Mock()
        chunk.data.skip(1)
        stream.seek.assert_not_called()

    def test_error_if_stream_has_no_seek_method(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        stream.seek = unittest.mock.Mock(side_effect=AttributeError)
        chunk = riff.Chunk.streamfrom(stream)
        with self.assertRaisesError('stream is not seekable'):
            chunk.data.skip(1)

    def test_error_if_stream_not_seekable(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        stream.seek = unittest.mock.Mock(side_effect=OSError)
        chunk = riff.Chunk.streamfrom(stream)
        with self.assertRaisesError('stream is not seekable'):
            chunk.data.skip(1)

    def test_stream_position_advanced(self):
        datastream = io.BytesIO(b'MockDataOdd\x00')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skip(4)
        self.assertEqual(4, datastream.tell())

    def test_stream_position_not_advanced_more_than_size_bytes(self):
        datastream = io.BytesIO(b'MockDataOdd\x00')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skip(12)
        self.assertEqual(11, datastream.tell())

    def test_stream_position_not_advanced_more_than_size_bytes_in_total(self):
        datastream = io.BytesIO(b'MockDataOdd\x00')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skip(4)
        chunk.data.skip(8)
        self.assertEqual(11, datastream.tell())


class Test_ChunkData_skipall(TestCase):
    def test_advances_position_to_end_from_start(self):
        datastream = io.BytesIO(b'MockDataOdd\x00')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skipall()
        self.assertEqual(11, chunk.data.position)

    def test_advances_position_to_end_from_current_position(self):
        datastream = io.BytesIO(b'MockDataOdd\x00')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skip(4)
        chunk.data.skipall()
        self.assertEqual(11, chunk.data.position)

    def test_advances_stream_position_to_end_from_start(self):
        datastream = io.BytesIO(b'MockDataOdd\x00')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skipall()
        self.assertEqual(11, datastream.tell())

    def test_advances_stream_position_to_end_from_current_position(self):
        datastream = io.BytesIO(b'MockDataOdd\x00')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        chunk.data.skip(4)
        chunk.data.skipall()
        self.assertEqual(11, datastream.tell())

    def test_consumes_chunk_data(self):
        stream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(stream)
        chunk.data.skipall()
        self.assertTrue(chunk.data.consumed)

    def test_error_if_stream_has_no_seek_method(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        stream.seek = unittest.mock.Mock(side_effect=AttributeError)
        chunk = riff.Chunk.streamfrom(stream)
        with self.assertRaisesError('stream is not seekable'):
            chunk.data.skipall()

    def test_error_if_stream_not_seekable(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        stream.seek = unittest.mock.Mock(side_effect=OSError)
        chunk = riff.Chunk.streamfrom(stream)
        with self.assertRaisesError('stream is not seekable'):
            chunk.data.skipall()


class Test_ChunkData_writeto(TestCase):
    def test_error_if_chunk_data_partially_consumed(self):
        instream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(instream)
        chunk.data.skip(4)
        outstream = io.BytesIO()
        with self.assertRaisesError('chunk data partially consumed'):
            chunk.data.writeto(outstream)

    def test_read_then_write_preserves_bytes(self):
        indatastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, indatastream)
        outdatastream = io.BytesIO()
        chunk.data.writeto(outdatastream)
        self.assertEqual(indatastream.getvalue(), outdatastream.getvalue())

    def test_does_not_read_more_than_buffer_size_bytes_at_once(self):
        indatastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, indatastream)
        indatastream.read = unittest.mock.Mock()
        indatastream.read.side_effect = lambda size: b'\x00' * size
        outdatastream = io.BytesIO()
        chunk.data.writeto(outdatastream, buffersize=4)
        read_sizes = [args[0] for args, _ in indatastream.read.call_args_list]
        self.assertTrue(all(size <= 4 for size in read_sizes))


class Test_ChunkData_repr(TestCase):
    def test_for_unpadded_chunk(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertEqual("riff.ChunkData(size=8)", repr(chunk.data))

    def test_for_padded_chunk(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        self.assertEqual("riff.ChunkData(size=11)", repr(chunk.data))


class Test_StreamSection_enter(TestCase):
    def test_returns_self(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        with section as context:
            self.assertIs(section, context)

    def test_error_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        section.close()
        with self.assertRaises(ValueError):
            with section:
                pass


class Test_StreamSection_exit(TestCase):
    def test_closes_self(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        with section:
            pass
        self.assertTrue(section.closed)

    def test_does_not_close_stream(self):
        stream = io.BytesIO(b'SomeMockTestData')
        with riff.StreamSection(stream, 8):
            pass
        self.assertFalse(stream.closed)


class Test_StreamSection_close(TestCase):
    def test_closes_self(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        section.close()
        self.assertTrue(section.closed)

    def test_can_be_called_multiple_times(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        section.close()
        section.close()

    def test_does_not_close_stream(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        section.close()
        self.assertFalse(stream.closed)


class Test_StreamSection_closed(TestCase):
    def test_False_after_init(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        self.assertFalse(section.closed)

    def test_True_after_closing(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        section.close()
        self.assertTrue(section.closed)

    def test_True_after_exiting_context_manager(self):
        stream = io.BytesIO(b'SomeMockTestData')
        with riff.StreamSection(stream, 8) as section:
            pass
        self.assertTrue(section.closed)


class Test_StreamSection_fileno(TestCase):
    def test_returns_stream_fileno(self):
        stream = io.BytesIO(b'SomeMockTestData')
        mock = unittest.mock.Mock()
        stream.fileno = unittest.mock.Mock(return_value=mock)
        section = riff.StreamSection(stream, 8)
        self.assertEqual(mock, section.fileno())

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.fileno = unittest.mock.Mock()
        section = riff.StreamSection(stream, 8)
        section.close()
        with self.assertRaises(ValueError) as context:
            section.fileno()
        self.assertEqual('stream closed', str(context.exception))


class Test_StreamSection_flush(TestCase):
    def test_does_not_raise_error(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        section.flush()

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        section.close()
        with self.assertRaises(ValueError) as context:
            section.flush()
        self.assertEqual('stream closed', str(context.exception))


class Test_StreamSection_isatty(TestCase):
    def test_returns_whether_stream_isatty(self):
        stream = io.BytesIO(b'SomeMockTestData')
        mock = unittest.mock.Mock()
        stream.isatty = unittest.mock.Mock(return_value=mock)
        section = riff.StreamSection(stream, 8)
        self.assertEqual(mock, section.isatty())

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.isatty = unittest.mock.Mock()
        section = riff.StreamSection(stream, 8)
        section.close()
        with self.assertRaises(ValueError) as context:
            section.isatty()
        self.assertEqual('stream closed', str(context.exception))


class Test_StreamSection_read(TestCase):
    def test_reads_all_bytes_by_default(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        self.assertEqual(b'MockTest', section.read())

    def test_reads_all_bytes_for_negative_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        self.assertEqual(b'MockTest', section.read(-1))

    def test_reads_all_bytes_for_None_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        self.assertEqual(b'MockTest', section.read(None))

    def test_no_bytes_when_size_is_zero(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        self.assertEqual(b'', section.read(0))

    def test_read_part_of_stream(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        self.assertEqual(b'Mock', section.read(4))

    def test_reading_past_end_only_returns_size_bytes(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        self.assertEqual(b'MockTest', section.read(9))

    def test_reading_past_end_moves_cursor_to_end(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        section.read(9)
        self.assertEqual(8, section.tell())

    def test_reading_moves_cursor_forward_by_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        section.read(4)
        self.assertEqual(4, section.tell())

    def test_reading_all_moves_cursor_to_end(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        section.read()
        self.assertEqual(8, section.tell())

    def test_error_when_section_truncated(self):
        stream = io.BytesIO(b'SomeMoc')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        with self.assertRaisesError('truncated at position 3'):
            section.read(4)

    def test_advances_cursor_despite_truncation(self):
        stream = io.BytesIO(b'SomeMoc')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        try:
            section.read(4)
        except riff.Error:
            pass
        self.assertEqual(3, section.tell())

    def test_reads_from_cursor_position(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        section.seek(4)
        self.assertEqual(b'Test', section.read(4))


class Test_StreamSection_readable(TestCase):
    def test_returns_whether_stream_readable(self):
        stream = io.BytesIO(b'SomeMockTestData')
        mock = unittest.mock.Mock()
        stream.readable = unittest.mock.Mock(return_value=mock)
        section = riff.StreamSection(stream, 8)
        self.assertEqual(mock, section.readable())

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.readable = unittest.mock.Mock()
        section = riff.StreamSection(stream, 8)
        section.close()
        with self.assertRaises(ValueError) as context:
            section.readable()
        self.assertEqual('stream closed', str(context.exception))


class Test_StreamSection_seek(TestCase):
    def test_seeks_relative_to_start_by_default(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        section.seek(4)
        self.assertEqual(4, section.tell())

    def test_seek_relative_to_start(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        section.seek(4, io.SEEK_SET)
        self.assertEqual(4, section.tell())

    def test_seek_relative_to_start_constrained_by_start(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        section.seek(-1, io.SEEK_SET)
        self.assertEqual(0, section.tell())

    def test_seek_relative_to_start_constrained_by_end(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        section.seek(9, io.SEEK_SET)
        self.assertEqual(8, section.tell())

    def test_positive_seek_relative_to_current(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        section.seek(1)
        section.seek(4, io.SEEK_CUR)
        self.assertEqual(5, section.tell())

    def test_negative_seek_relative_to_current(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        section.seek(5)
        section.seek(-4, io.SEEK_CUR)
        self.assertEqual(1, section.tell())

    def test_seek_relative_to_current_constrained_by_start(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        section.seek(4)
        section.seek(-5, io.SEEK_CUR)
        self.assertEqual(0, section.tell())

    def test_seek_relative_to_current_constrained_by_end(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        section.seek(4)
        section.seek(5, io.SEEK_CUR)
        self.assertEqual(8, section.tell())

    def test_seek_relative_to_end(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        section.seek(-4, io.SEEK_END)
        self.assertEqual(4, section.tell())

    def test_seek_relative_to_end_constrained_by_start(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        section.seek(-9, io.SEEK_END)
        self.assertEqual(0, section.tell())

    def test_seek_relative_to_end_constrained_by_end(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        section.seek(1, io.SEEK_END)
        self.assertEqual(8, section.tell())

    def test_ValueError_for_invalid_whence(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        with self.assertRaises(ValueError) as context:
            section.seek(4, whence=3)
        self.assertEqual('invalid whence value', str(context.exception))

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        section.close()
        with self.assertRaises(ValueError) as context:
            section.seek(4)
        self.assertEqual('stream closed', str(context.exception))


class Test_StreamSection_size(TestCase):
    def test_returns_input_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        self.assertEqual(8, section.size)


class Test_StreamSection_tell(TestCase):
    def test_returns_zero_after_init(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        section = riff.StreamSection(stream, 8)
        self.assertEqual(0, section.tell())

    def test_returns_same_position_despite_stream_seek(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        section.seek(4, io.SEEK_SET)
        position_before = section.tell()
        stream.seek(10, io.SEEK_SET)
        self.assertEqual(position_before, section.tell())

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        section.close()
        with self.assertRaises(ValueError) as context:
            section.tell()
        self.assertEqual('stream closed', str(context.exception))


class Test_StreamSection_tell(TestCase):
    def test_raises_error_for_default_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        with self.assertRaises(io.UnsupportedOperation) as context:
            section.truncate()
        self.assertEqual('stream not writable', str(context.exception))

    def test_raises_error_when_size_specified(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        with self.assertRaises(io.UnsupportedOperation) as context:
            section.truncate(4)
        self.assertEqual('stream not writable', str(context.exception))

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        section = riff.StreamSection(stream, 8)
        section.close()
        with self.assertRaises(ValueError) as context:
            section.truncate()
        self.assertEqual('stream closed', str(context.exception))


if __name__ == '__main__':
    unittest.main()
