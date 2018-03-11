import io
import riff
import unittest
import unittest.mock


class Test_Chunk_create(unittest.TestCase):
    def test_returns_Chunk_instance(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertIsInstance(chunk, riff.Chunk)

    def test_no_error_with_empty_data_stream(self):
        datastream = io.BytesIO(b'')
        riff.Chunk.create('MOCK', 0, datastream)


class Test_Chunk_data(unittest.TestCase):
    def test_is_ChunkData_instance_after_creating_chunk(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertIsInstance(chunk.data, riff.ChunkData)

    def test_is_ChunkData_instance_after_reading_chunk_from_stream(self):
        iostream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(iostream, stream=True)
        self.assertIsInstance(chunk.data, riff.ChunkData)


class Test_Chunk_id(unittest.TestCase):
    def test_value_after_creating_chunk(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertEqual('MOCK', chunk.id)

    def test_value_after_reading_chunk_from_stream(self):
        iostream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(iostream, stream=True)
        self.assertEqual('MOCK', chunk.id)


class Test_Chunk_padded(unittest.TestCase):
    def test_True_if_size_odd_and_pad_byte_expected(self):
        iostream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.readfrom(iostream, stream=True)
        self.assertTrue(chunk.padded)

    def test_True_if_size_odd_and_pad_byte_not_expected(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        self.assertTrue(chunk.padded)

    def test_False_if_size_even_and_pad_byte_expected(self):
        iostream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(iostream, stream=True)
        self.assertFalse(chunk.padded)

    def test_False_if_size_even_and_pad_byte_not_expected(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertFalse(chunk.padded)


class Test_Chunk_readfrom(unittest.TestCase):
    def test_returns_Chunk_instance(self):
        iostream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(iostream)
        self.assertIsInstance(chunk, riff.Chunk)

    def test_no_error_with_empty_chunk(self):
        iostream = io.BytesIO(b'MOCK\x00\x00\x00\x00')
        riff.Chunk.readfrom(iostream)

    def test_error_when_id_truncated(self):
        iostream = io.BytesIO(b'MOC')
        with self.assertRaises(riff.Error) as ctx:
            riff.Chunk.readfrom(iostream)
        self.assertEqual('chunk header truncated', str(ctx.exception))

    def test_error_when_size_truncated(self):
        iostream = io.BytesIO(b'MOCK\x08\x00')
        with self.assertRaises(riff.Error) as ctx:
            riff.Chunk.readfrom(iostream)
        self.assertEqual('chunk header truncated', str(ctx.exception))

    def test_error_when_data_truncated(self):
        iostream = io.BytesIO(b'MOCK\x08\x00\x00\x00Mock')
        with self.assertRaises(riff.Error) as ctx:
            riff.Chunk.readfrom(iostream)
        self.assertEqual('chunk data truncated', str(ctx.exception))

    def test_no_truncation_error_when_streaming(self):
        iostream = io.BytesIO(b'MOCK\x08\x00\x00\x00Mock')
        riff.Chunk.readfrom(iostream, stream=True)

    def test_error_when_id_not_ascii(self):
        iostream = io.BytesIO(b'M\xffCK\x08\x00\x00\x00MockData')
        with self.assertRaises(riff.Error) as ctx:
            riff.Chunk.readfrom(iostream)
        self.assertEqual('chunk id not ascii-decodable', str(ctx.exception))

    def test_can_read_data_after_closing_iostream(self):
        iostream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(iostream)
        iostream.close()
        self.assertEqual(b'Mock', chunk.data.read(4))


class Test_Chunk_repr(unittest.TestCase):
    def test_for_unpadded_chunk_read_from_stream(self):
        iostream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(iostream, stream=True)
        self.assertEqual("riff.Chunk(id='MOCK', size=8)", repr(chunk))

    def test_for_padded_chunk_read_from_stream(self):
        iostream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.readfrom(iostream, stream=True)
        self.assertEqual("riff.Chunk(id='MOCK', size=11)", repr(chunk))

    def test_for_unpadded_created_chunk(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertEqual("riff.Chunk(id='MOCK', size=8)", repr(chunk))

    def test_for_padded_created_chunk(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        self.assertEqual("riff.Chunk(id='MOCK', size=11)", repr(chunk))


class Test_Chunk_size(unittest.TestCase):
    def test_value_after_creating_unpadded_chunk(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertEqual(8, chunk.size)

    def test_value_after_reading_unpadded_chunk_from_stream(self):
        iostream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(iostream, stream=True)
        self.assertEqual(8, chunk.size)

    def test_value_after_creating_padded_chunk(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        self.assertEqual(11, chunk.size)

    def test_value_after_reading_padded_chunk_from_stream(self):
        iostream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.readfrom(iostream, stream=True)
        self.assertEqual(11, chunk.size)


class Test_ChunkData_close(unittest.TestCase):
    def test_closes_self(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.close()
        self.assertTrue(data.closed)

    def test_can_be_called_multiple_times(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.close()
        data.close()

    def test_does_not_close_stream(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.close()
        self.assertFalse(iostream.closed)


class Test_ChunkData_exit(unittest.TestCase):
    def test_closes_self(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        with data:
            pass
        self.assertTrue(data.closed)

    def test_does_not_close_stream(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        with riff.ChunkData.streamfrom(iostream, size=8):
            pass
        self.assertFalse(iostream.closed)


class Test_ChunkData_next(unittest.TestCase):
    def test_reads_line(self):
        iostream = io.BytesIO(b'SomeMock\nTest\nData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=10)
        self.assertEqual(b'Mock\n', next(data))

    def test_does_not_read_past_data_end(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertEqual(b'MockTest', next(data))

    def test_does_not_read_past_data_end_after_seek(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(4)
        self.assertEqual(b'Test', next(data))

    def test_error_if_closed(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            next(data)
        self.assertEqual('io stream closed', str(ctx.exception))


class Test_ChunkData_read(unittest.TestCase):
    def test_reads_all_bytes_by_default(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertEqual(b'MockTest', data.read())

    def test_reads_all_bytes_for_negative_size(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertEqual(b'MockTest', data.read(-1))

    def test_reads_all_bytes_for_None_size(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertEqual(b'MockTest', data.read(None))

    def test_no_bytes_when_size_is_zero(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertEqual(b'', data.read(0))

    def test_read_part_of_stream(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertEqual(b'Mock', data.read(4))

    def test_reading_past_end_only_returns_size_bytes(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertEqual(b'MockTest', data.read(9))

    def test_reading_past_end_moves_cursor_to_end(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.read(9)
        self.assertEqual(8, data.tell())

    def test_reading_moves_cursor_forward_by_size(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.read(4)
        self.assertEqual(4, data.tell())

    def test_reading_all_moves_cursor_to_end(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.read()
        self.assertEqual(8, data.tell())

    def test_error_when_data_truncated(self):
        iostream = io.BytesIO(b'SomeMoc')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        with self.assertRaises(riff.Error) as ctx:
            data.read(4)
        self.assertEqual('truncated at position 3', str(ctx.exception))

    def test_advances_cursor_despite_truncation(self):
        iostream = io.BytesIO(b'SomeMoc')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        try:
            data.read(4)
        except riff.Error:
            pass
        self.assertEqual(3, data.tell())

    def test_reads_from_cursor_position(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(4)
        self.assertEqual(b'Test', data.read(4))

    def test_ValueError_if_closed(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.read(4)
        self.assertEqual('io stream closed', str(ctx.exception))


class Test_ChunkData_readinto(unittest.TestCase):
    def test_reads_zero_bytes_into_empty_bytearray(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        buffer = bytearray()
        self.assertEqual(0, data.readinto(buffer))
        self.assertEqual(b'', bytes(buffer))

    def test_reads_zero_bytes_into_empty_memoryview(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        buffer = memoryview(bytearray())
        self.assertEqual(0, data.readinto(buffer))
        self.assertEqual(b'', bytes(buffer.obj))

    def test_reads_multiple_bytes_into_bytearray(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        buffer = bytearray(4)
        self.assertEqual(4, data.readinto(buffer))
        self.assertEqual(b'Mock', bytes(buffer))

    def test_reads_multiple_bytes_into_memoryview(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        buffer = memoryview(bytearray(4))
        self.assertEqual(4, data.readinto(buffer))
        self.assertEqual(b'Mock', bytes(buffer.obj))

    def test_only_reads_size_bytes_if_buffer_bigger_than_size(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        buffer = bytearray(10)
        self.assertEqual(8, data.readinto(buffer))
        self.assertEqual(b'MockTest\x00\x00', bytes(buffer))

    def test_moves_cursor_to_end_if_buffer_bigger_than_size(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.readinto(bytearray(9))
        self.assertEqual(8, data.tell())

    def test_moves_cursor_forward_by_buffer_size(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.readinto(bytearray(4))
        self.assertEqual(4, data.tell())

    def test_error_when_data_truncated(self):
        iostream = io.BytesIO(b'SomeMoc')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        with self.assertRaises(riff.Error) as ctx:
            data.readinto(bytearray(4))
        self.assertEqual('truncated at position 3', str(ctx.exception))

    def test_advances_cursor_despite_truncation(self):
        iostream = io.BytesIO(b'SomeMoc')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        try:
            data.readinto(bytearray(4))
        except riff.Error:
            pass
        self.assertEqual(3, data.tell())

    def test_reads_from_cursor_position(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(4)
        buffer = bytearray(4)
        self.assertEqual(4, data.readinto(buffer))
        self.assertEqual(b'Test', bytes(buffer))

    def test_ValueError_if_closed(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.readinto(bytearray())
        self.assertEqual('io stream closed', str(ctx.exception))


class Test_ChunkData_readline(unittest.TestCase):
    def test_reads_line_with_no_limit(self):
        iostream = io.BytesIO(b'SomeMock\nTest\nData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=10)
        self.assertEqual(b'Mock\n', data.readline())

    def test_reads_line_with_None_limit(self):
        iostream = io.BytesIO(b'SomeMock\nTest\nData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=10)
        self.assertEqual(b'Mock\n', data.readline(None))

    def test_reads_line_with_negative_limit(self):
        iostream = io.BytesIO(b'SomeMock\nTest\nData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=10)
        self.assertEqual(b'Mock\n', data.readline(-1))

    def test_does_not_read_past_zero_byte_limit(self):
        iostream = io.BytesIO(b'SomeMock\nTest\nData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=10)
        self.assertEqual(b'', data.readline(0))

    def test_does_not_read_past_positive_byte_limit(self):
        iostream = io.BytesIO(b'SomeMock\nTest\nData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=10)
        self.assertEqual(b'Mo', data.readline(2))

    def test_does_not_read_past_data_end_with_no_limit(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertEqual(b'MockTest', data.readline())

    def test_does_not_read_past_data_end_after_seek(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(4)
        self.assertEqual(b'Test', data.readline())

    def test_does_not_read_past_data_end_with_limit(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertEqual(b'MockTest', data.readline(12))

    def test_ValueError_if_closed(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.readline()
        self.assertEqual('io stream closed', str(ctx.exception))


class Test_ChunkData_repr(unittest.TestCase):
    def test(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertEqual("riff.ChunkData(size=8)", repr(data))


class Test_ChunkData_seek(unittest.TestCase):
    def test_seeks_relative_to_start_by_default(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(4)
        self.assertEqual(4, data.tell())

    def test_seek_relative_to_start(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(4, io.SEEK_SET)
        self.assertEqual(4, data.tell())

    def test_seek_relative_to_start_constrained_by_start(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(-1, io.SEEK_SET)
        self.assertEqual(0, data.tell())

    def test_seek_relative_to_start_constrained_by_end(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(9, io.SEEK_SET)
        self.assertEqual(8, data.tell())

    def test_positive_seek_relative_to_current(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(1)
        data.seek(4, io.SEEK_CUR)
        self.assertEqual(5, data.tell())

    def test_negative_seek_relative_to_current(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(5)
        data.seek(-4, io.SEEK_CUR)
        self.assertEqual(1, data.tell())

    def test_seek_relative_to_current_constrained_by_start(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(4)
        data.seek(-5, io.SEEK_CUR)
        self.assertEqual(0, data.tell())

    def test_seek_relative_to_current_constrained_by_end(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(4)
        data.seek(5, io.SEEK_CUR)
        self.assertEqual(8, data.tell())

    def test_seek_relative_to_end(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(-4, io.SEEK_END)
        self.assertEqual(4, data.tell())

    def test_seek_relative_to_end_constrained_by_start(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(-9, io.SEEK_END)
        self.assertEqual(0, data.tell())

    def test_seek_relative_to_end_constrained_by_end(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(1, io.SEEK_END)
        self.assertEqual(8, data.tell())

    def test_ValueError_for_invalid_whence(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        with self.assertRaises(ValueError) as ctx:
            data.seek(4, whence=3)
        self.assertEqual('invalid whence value', str(ctx.exception))

    def test_ValueError_if_closed(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.seek(4)
        self.assertEqual('io stream closed', str(ctx.exception))


class Test_ChunkData_size(unittest.TestCase):
    def test_returns_input_size(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertEqual(8, data.size)


class Test_ChunkData_streamfrom(unittest.TestCase):
    def test_reads_from_start_position(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertEqual(b'Mock', data.read(4))

    def test_advances_stream_cursor_by_size(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertEqual(12, iostream.tell())

    def test_not_closed_after_init(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertFalse(data.closed)

    def test_size_property_matches_input_size(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertEqual(8, data.size)


class Test_ChunkData_tell(unittest.TestCase):
    def test_returns_zero_after_init(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertEqual(0, data.tell())

    def test_returns_same_position_despite_stream_seek(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.seek(4, io.SEEK_SET)
        position_before = data.tell()
        iostream.seek(10, io.SEEK_SET)
        self.assertEqual(position_before, data.tell())

    def test_ValueError_if_closed(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.tell()
        self.assertEqual('io stream closed', str(ctx.exception))


class Test_ChunkData_truncate(unittest.TestCase):
    def test_raises_error_for_default_size(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        with self.assertRaises(io.UnsupportedOperation) as ctx:
            data.truncate()
        self.assertEqual('io stream not writable', str(ctx.exception))

    def test_raises_error_when_size_specified(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        with self.assertRaises(io.UnsupportedOperation) as ctx:
            data.truncate(4)
        self.assertEqual('io stream not writable', str(ctx.exception))

    def test_ValueError_if_closed(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.truncate()
        self.assertEqual('io stream closed', str(ctx.exception))


class Test_ChunkData_writable(unittest.TestCase):
    def test_returns_False_despite_writable_stream(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.writable = unittest.mock.Mock(return_value=True)
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        self.assertFalse(data.writable())

    def test_ValueError_if_closed(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.writable()
        self.assertEqual('io stream closed', str(ctx.exception))


class Test_ChunkData_writelines(unittest.TestCase):
    def test_raises_error(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        with self.assertRaises(io.UnsupportedOperation) as ctx:
            data.writelines([b'Line1\n', b'Line2\n'])
        self.assertEqual('io stream not writable', str(ctx.exception))

    def test_does_not_call_stream_writelines_method(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.writelines = unittest.mock.Mock()
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        try:
            data.writelines([b'Line1\n', b'Line2\n'])
        except io.UnsupportedOperation:
            pass
        iostream.writelines.assert_not_called()

    def test_ValueError_if_closed(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.writelines([b'Line1\n', b'Line2\n'])
        self.assertEqual('io stream closed', str(ctx.exception))


class Test_ChunkData_write(unittest.TestCase):
    def test_raises_error(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        with self.assertRaises(io.UnsupportedOperation) as ctx:
            data.write(b'Data')
        self.assertEqual('io stream not writable', str(ctx.exception))

    def test_does_not_call_stream_write_method(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.write = unittest.mock.Mock()
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        try:
            data.write(b'Data')
        except io.UnsupportedOperation:
            pass
        iostream.write.assert_not_called()

    def test_ValueError_if_closed(self):
        iostream = io.BytesIO(b'SomeMockTestData')
        iostream.seek(4)
        data = riff.ChunkData.streamfrom(iostream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.write(b'Data')
        self.assertEqual('io stream closed', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
