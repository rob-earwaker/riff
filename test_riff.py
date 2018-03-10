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
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertIsInstance(chunk.data, riff.ChunkData)


class Test_Chunk_id(unittest.TestCase):
    def test_value_after_creating_chunk(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertEqual('MOCK', chunk.id)

    def test_value_after_reading_chunk_from_stream(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertEqual('MOCK', chunk.id)


class Test_Chunk_padded(unittest.TestCase):
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


class Test_Chunk_readfrom(unittest.TestCase):
    def test_returns_Chunk_instance(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.readfrom(stream)
        self.assertIsInstance(chunk, riff.Chunk)

    def test_no_error_with_empty_chunk(self):
        stream = io.BytesIO(b'MOCK\x00\x00\x00\x00')
        riff.Chunk.readfrom(stream)

    def test_error_when_id_truncated(self):
        stream = io.BytesIO(b'MOC')
        with self.assertRaises(riff.Error) as ctx:
            riff.Chunk.readfrom(stream)
        self.assertEqual('chunk header truncated', str(ctx.exception))

    def test_error_when_size_truncated(self):
        stream = io.BytesIO(b'MOCK\x08\x00')
        with self.assertRaises(riff.Error) as ctx:
            riff.Chunk.readfrom(stream)
        self.assertEqual('chunk header truncated', str(ctx.exception))

    def test_error_when_id_not_ascii(self):
        stream = io.BytesIO(b'M\xffCK\x08\x00\x00\x00MockData')
        with self.assertRaises(riff.Error) as ctx:
            riff.Chunk.readfrom(stream)
        self.assertEqual('chunk id not ascii-decodable', str(ctx.exception))


class Test_Chunk_repr(unittest.TestCase):
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


class Test_Chunk_size(unittest.TestCase):
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


class Test_Chunk_streamfrom(unittest.TestCase):
    def test_returns_Chunk_instance(self):
        stream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(stream)
        self.assertIsInstance(chunk, riff.Chunk)

    def test_no_error_with_empty_chunk(self):
        stream = io.BytesIO(b'MOCK\x00\x00\x00\x00')
        riff.Chunk.streamfrom(stream)

    def test_error_when_id_truncated(self):
        stream = io.BytesIO(b'MOC')
        with self.assertRaises(riff.Error) as ctx:
            riff.Chunk.streamfrom(stream)
        self.assertEqual('chunk header truncated', str(ctx.exception))

    def test_error_when_size_truncated(self):
        stream = io.BytesIO(b'MOCK\x08\x00')
        with self.assertRaises(riff.Error) as ctx:
            riff.Chunk.streamfrom(stream)
        self.assertEqual('chunk header truncated', str(ctx.exception))

    def test_error_when_id_not_ascii(self):
        stream = io.BytesIO(b'M\xffCK\x08\x00\x00\x00MockData')
        with self.assertRaises(riff.Error) as ctx:
            riff.Chunk.streamfrom(stream)
        self.assertEqual('chunk id not ascii-decodable', str(ctx.exception))


class Test_ChunkData_close(unittest.TestCase):
    def test_closes_self(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        self.assertTrue(data.closed)

    def test_can_be_called_multiple_times(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        data.close()

    def test_does_not_close_stream(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        self.assertFalse(stream.closed)


class Test_ChunkData_closed(unittest.TestCase):
    def test_False_after_init(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertFalse(data.closed)

    def test_True_after_closing(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        self.assertTrue(data.closed)

    def test_True_after_closing_stream(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        stream.close()
        self.assertTrue(data.closed)

    def test_True_after_exiting_ctx_manager(self):
        stream = io.BytesIO(b'SomeMockTestData')
        with riff.ChunkData.streamfrom(stream, size=8) as data:
            pass
        self.assertTrue(data.closed)


class Test_ChunkData_enter(unittest.TestCase):
    def test_returns_self(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        with data as ctx:
            self.assertIs(data, ctx)

    def test_error_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            with data:
                pass
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_exit(unittest.TestCase):
    def test_closes_self(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        with data:
            pass
        self.assertTrue(data.closed)

    def test_does_not_close_stream(self):
        stream = io.BytesIO(b'SomeMockTestData')
        with riff.ChunkData.streamfrom(stream, size=8):
            pass
        self.assertFalse(stream.closed)


class Test_ChunkData_detach(unittest.TestCase):
    def test_raises_error(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        with self.assertRaises(io.UnsupportedOperation) as ctx:
            data.detach()
        self.assertEqual('stream not detachable', str(ctx.exception))

    def test_does_not_call_stream_detach_method(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.detach = unittest.mock.Mock()
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        try:
            data.detach()
        except io.UnsupportedOperation:
            pass
        stream.detach.assert_not_called()

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.detach()
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_fileno(unittest.TestCase):
    def test_returns_stream_fileno(self):
        stream = io.BytesIO(b'SomeMockTestData')
        mock = unittest.mock.Mock()
        stream.fileno = unittest.mock.Mock(return_value=mock)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(mock, data.fileno())

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.fileno = unittest.mock.Mock()
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.fileno()
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_flush(unittest.TestCase):
    def test_does_not_raise_error(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.flush()

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.flush()
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_isatty(unittest.TestCase):
    def test_returns_whether_stream_isatty(self):
        stream = io.BytesIO(b'SomeMockTestData')
        mock = unittest.mock.Mock()
        stream.isatty = unittest.mock.Mock(return_value=mock)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(mock, data.isatty())

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.isatty = unittest.mock.Mock()
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.isatty()
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_iter(unittest.TestCase):
    def test_returns_self(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertIs(data, iter(data))

    def test_error_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            iter(data)
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_next(unittest.TestCase):
    def test_reads_line(self):
        stream = io.BytesIO(b'SomeMock\nTest\nData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=10)
        self.assertEqual(b'Mock\n', next(data))

    def test_does_not_read_past_data_end(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'MockTest', next(data))

    def test_does_not_read_past_data_end_after_seek(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(4)
        self.assertEqual(b'Test', next(data))

    def test_error_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            next(data)
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_read(unittest.TestCase):
    def test_reads_all_bytes_by_default(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'MockTest', data.read())

    def test_reads_all_bytes_for_negative_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'MockTest', data.read(-1))

    def test_reads_all_bytes_for_None_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'MockTest', data.read(None))

    def test_no_bytes_when_size_is_zero(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'', data.read(0))

    def test_read_part_of_stream(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'Mock', data.read(4))

    def test_reading_past_end_only_returns_size_bytes(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'MockTest', data.read(9))

    def test_reading_past_end_moves_cursor_to_end(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.read(9)
        self.assertEqual(8, data.tell())

    def test_reading_moves_cursor_forward_by_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.read(4)
        self.assertEqual(4, data.tell())

    def test_reading_all_moves_cursor_to_end(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.read()
        self.assertEqual(8, data.tell())

    def test_error_when_data_truncated(self):
        stream = io.BytesIO(b'SomeMoc')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        with self.assertRaises(riff.Error) as ctx:
            data.read(4)
        self.assertEqual('truncated at position 3', str(ctx.exception))

    def test_advances_cursor_despite_truncation(self):
        stream = io.BytesIO(b'SomeMoc')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        try:
            data.read(4)
        except riff.Error:
            pass
        self.assertEqual(3, data.tell())

    def test_reads_from_cursor_position(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(4)
        self.assertEqual(b'Test', data.read(4))

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.read(4)
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_read1(unittest.TestCase):
    def test_does_not_require_raw_stream_read1_attr(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.read1 = unittest.mock.Mock(side_effect=AttributeError)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'MockTest', data.read1())

    def test_reads_all_bytes_by_default(self):
        raw = io.BytesIO(b'SomeMockTestData')
        stream = io.BufferedReader(raw, buffer_size=4)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'MockTest', data.read1())

    def test_reads_all_bytes_for_negative_size(self):
        raw = io.BytesIO(b'SomeMockTestData')
        stream = io.BufferedReader(raw, buffer_size=4)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'MockTest', data.read1(-1))

    def test_reads_all_bytes_for_None_size(self):
        raw = io.BytesIO(b'SomeMockTestData')
        stream = io.BufferedReader(raw, buffer_size=4)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'MockTest', data.read1(None))

    def test_no_bytes_when_size_is_zero(self):
        raw = io.BytesIO(b'SomeMockTestData')
        stream = io.BufferedReader(raw, buffer_size=4)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'', data.read1(0))

    def test_read_less_than_buffer_size_bytes(self):
        raw = io.BytesIO(b'SomeMockTestData')
        stream = io.BufferedReader(raw, buffer_size=5)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'Mock', data.read1(4))

    def test_read_more_than_buffer_size_bytes(self):
        raw = io.BytesIO(b'SomeMockTestData')
        stream = io.BufferedReader(raw, buffer_size=3)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'Mock', data.read1(4))

    def test_reading_past_end_only_returns_size_bytes(self):
        raw = io.BytesIO(b'SomeMockTestData')
        stream = io.BufferedReader(raw, buffer_size=4)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'MockTest', data.read1(9))

    def test_reading_past_end_moves_cursor_to_end(self):
        raw = io.BytesIO(b'SomeMockTestData')
        stream = io.BufferedReader(raw, buffer_size=4)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.read1(9)
        self.assertEqual(8, data.tell())

    def test_reading_moves_cursor_forward_by_size(self):
        raw = io.BytesIO(b'SomeMockTestData')
        stream = io.BufferedReader(raw, buffer_size=4)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.read1(4)
        self.assertEqual(4, data.tell())

    def test_reading_all_moves_cursor_to_end(self):
        raw = io.BytesIO(b'SomeMockTestData')
        stream = io.BufferedReader(raw, buffer_size=4)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.read1()
        self.assertEqual(8, data.tell())

    def test_error_when_data_truncated(self):
        raw = io.BytesIO(b'SomeMoc')
        stream = io.BufferedReader(raw, buffer_size=4)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        with self.assertRaises(riff.Error) as ctx:
            data.read1(4)
        self.assertEqual('truncated at position 3', str(ctx.exception))

    def test_advances_cursor_despite_truncation(self):
        raw = io.BytesIO(b'SomeMoc')
        stream = io.BufferedReader(raw, buffer_size=4)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        try:
            data.read1(4)
        except riff.Error:
            pass
        self.assertEqual(3, data.tell())

    def test_reads_from_cursor_position(self):
        raw = io.BytesIO(b'SomeMockTestData')
        stream = io.BufferedReader(raw, buffer_size=4)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(4)
        self.assertEqual(b'Test', data.read1(4))

    def test_ValueError_if_closed(self):
        raw = io.BytesIO(b'SomeMockTestData')
        stream = io.BufferedReader(raw, buffer_size=4)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.read1(4)
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_readable(unittest.TestCase):
    def test_returns_whether_stream_readable(self):
        stream = io.BytesIO(b'SomeMockTestData')
        mock = unittest.mock.Mock()
        stream.readable = unittest.mock.Mock(return_value=mock)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(mock, data.readable())

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.readable = unittest.mock.Mock()
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.readable()
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_readfrom(unittest.TestCase):
    def test_not_closed_when_stream_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.readfrom(stream, size=8)
        stream.close()
        self.assertFalse(data.closed)

    def test_reads_from_start_position(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.readfrom(stream, size=8)
        self.assertEqual(b'Mock', data.read(4))

    def test_advances_stream_cursor_by_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.readfrom(stream, size=8)
        self.assertEqual(12, stream.tell())

    def test_error_if_truncated(self):
        stream = io.BytesIO(b'SomeMoc')
        stream.seek(4)
        with self.assertRaises(riff.Error) as ctx:
            riff.ChunkData.readfrom(stream, size=8)
        self.assertEqual('truncated at position 3', str(ctx.exception))

    def test_not_closed_after_init(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.readfrom(stream, size=8)
        self.assertFalse(data.closed)

    def test_size_property_matches_input_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.readfrom(stream, size=8)
        self.assertEqual(8, data.size)


class Test_ChunkData_readinto(unittest.TestCase):
    def test_reads_zero_bytes_into_empty_bytearray(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        buffer = bytearray()
        self.assertEqual(0, data.readinto(buffer))
        self.assertEqual(b'', bytes(buffer))

    def test_reads_zero_bytes_into_empty_memoryview(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        buffer = memoryview(bytearray())
        self.assertEqual(0, data.readinto(buffer))
        self.assertEqual(b'', bytes(buffer.obj))

    def test_reads_multiple_bytes_into_bytearray(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        buffer = bytearray(4)
        self.assertEqual(4, data.readinto(buffer))
        self.assertEqual(b'Mock', bytes(buffer))

    def test_reads_multiple_bytes_into_memoryview(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        buffer = memoryview(bytearray(4))
        self.assertEqual(4, data.readinto(buffer))
        self.assertEqual(b'Mock', bytes(buffer.obj))

    def test_only_reads_size_bytes_if_buffer_bigger_than_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        buffer = bytearray(10)
        self.assertEqual(8, data.readinto(buffer))
        self.assertEqual(b'MockTest\x00\x00', bytes(buffer))

    def test_moves_cursor_to_end_if_buffer_bigger_than_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.readinto(bytearray(9))
        self.assertEqual(8, data.tell())

    def test_moves_cursor_forward_by_buffer_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.readinto(bytearray(4))
        self.assertEqual(4, data.tell())

    def test_error_when_data_truncated(self):
        stream = io.BytesIO(b'SomeMoc')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        with self.assertRaises(riff.Error) as ctx:
            data.readinto(bytearray(4))
        self.assertEqual('truncated at position 3', str(ctx.exception))

    def test_advances_cursor_despite_truncation(self):
        stream = io.BytesIO(b'SomeMoc')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        try:
            data.readinto(bytearray(4))
        except riff.Error:
            pass
        self.assertEqual(3, data.tell())

    def test_reads_from_cursor_position(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(4)
        buffer = bytearray(4)
        self.assertEqual(4, data.readinto(buffer))
        self.assertEqual(b'Test', bytes(buffer))

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.readinto(bytearray())
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_readinto1(unittest.TestCase):
    def test_reads_zero_bytes_into_empty_bytearray(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        buffer = bytearray()
        self.assertEqual(0, data.readinto1(buffer))
        self.assertEqual(b'', bytes(buffer))

    def test_reads_zero_bytes_into_empty_memoryview(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        buffer = memoryview(bytearray())
        self.assertEqual(0, data.readinto1(buffer))
        self.assertEqual(b'', bytes(buffer.obj))

    def test_reads_multiple_bytes_into_bytearray(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        buffer = bytearray(4)
        self.assertEqual(4, data.readinto1(buffer))
        self.assertEqual(b'Mock', bytes(buffer))

    def test_reads_multiple_bytes_into_memoryview(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        buffer = memoryview(bytearray(4))
        self.assertEqual(4, data.readinto1(buffer))
        self.assertEqual(b'Mock', bytes(buffer.obj))

    def test_only_reads_size_bytes_if_buffer_bigger_than_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        buffer = bytearray(10)
        self.assertEqual(8, data.readinto1(buffer))
        self.assertEqual(b'MockTest\x00\x00', bytes(buffer))

    def test_moves_cursor_to_end_if_buffer_bigger_than_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.readinto1(bytearray(9))
        self.assertEqual(8, data.tell())

    def test_moves_cursor_forward_by_buffer_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.readinto1(bytearray(4))
        self.assertEqual(4, data.tell())

    def test_error_when_data_truncated(self):
        stream = io.BytesIO(b'SomeMoc')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        with self.assertRaises(riff.Error) as ctx:
            data.readinto1(bytearray(4))
        self.assertEqual('truncated at position 3', str(ctx.exception))

    def test_advances_cursor_despite_truncation(self):
        stream = io.BytesIO(b'SomeMoc')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        try:
            data.readinto1(bytearray(4))
        except riff.Error:
            pass
        self.assertEqual(3, data.tell())

    def test_reads_from_cursor_position(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(4)
        buffer = bytearray(4)
        self.assertEqual(4, data.readinto1(buffer))
        self.assertEqual(b'Test', bytes(buffer))

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.readinto1(bytearray())
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_readline(unittest.TestCase):
    def test_reads_line_with_no_limit(self):
        stream = io.BytesIO(b'SomeMock\nTest\nData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=10)
        self.assertEqual(b'Mock\n', data.readline())

    def test_reads_line_with_None_limit(self):
        stream = io.BytesIO(b'SomeMock\nTest\nData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=10)
        self.assertEqual(b'Mock\n', data.readline(None))

    def test_reads_line_with_negative_limit(self):
        stream = io.BytesIO(b'SomeMock\nTest\nData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=10)
        self.assertEqual(b'Mock\n', data.readline(-1))

    def test_does_not_read_past_zero_byte_limit(self):
        stream = io.BytesIO(b'SomeMock\nTest\nData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=10)
        self.assertEqual(b'', data.readline(0))

    def test_does_not_read_past_positive_byte_limit(self):
        stream = io.BytesIO(b'SomeMock\nTest\nData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=10)
        self.assertEqual(b'Mo', data.readline(2))

    def test_does_not_read_past_data_end_with_no_limit(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'MockTest', data.readline())

    def test_does_not_read_past_data_end_after_seek(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(4)
        self.assertEqual(b'Test', data.readline())

    def test_does_not_read_past_data_end_with_limit(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'MockTest', data.readline(12))

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.readline()
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_readlines(unittest.TestCase):
    def test_reads_lines_with_no_hint(self):
        stream = io.BytesIO(b'SomeMock\nTest\nData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=10)
        self.assertEqual([b'Mock\n', b'Test\n'], data.readlines())

    def test_reads_lines_with_None_hint(self):
        stream = io.BytesIO(b'SomeMock\nTest\nData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=10)
        self.assertEqual([b'Mock\n', b'Test\n'], data.readlines(None))

    def test_reads_lines_with_negative_hint(self):
        stream = io.BytesIO(b'SomeMock\nTest\nData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=10)
        self.assertEqual([b'Mock\n', b'Test\n'], data.readlines(-1))

    def test_reads_single_line_for_zero_hint(self):
        stream = io.BytesIO(b'SomeMock\nTest\nData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=10)
        self.assertEqual([b'Mock\n'], data.readlines(0))

    def test_does_reads_single_line_when_hint_less_than_line_size(self):
        stream = io.BytesIO(b'SomeMock\nTest\nData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=10)
        self.assertEqual([b'Mock\n'], data.readlines(2))

    def test_does_reads_multiple_lines_with_positive_hint(self):
        stream = io.BytesIO(b'SomeMock\nTest\nData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=10)
        self.assertEqual([b'Mock\n', b'Test\n'], data.readlines(7))

    def test_does_not_read_past_data_end_with_no_hint(self):
        stream = io.BytesIO(b'SomeMock\nTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=9)
        self.assertEqual([b'Mock\n', b'Test'], data.readlines())

    def test_does_not_read_past_data_end_after_seek(self):
        stream = io.BytesIO(b'SomeMock\nTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=9)
        data.seek(2)
        self.assertEqual([b'ck\n', b'Test'], data.readlines())

    def test_does_not_read_past_data_end_with_positive_hint(self):
        stream = io.BytesIO(b'SomeMock\nTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=9)
        self.assertEqual([b'Mock\n', b'Test'], data.readlines(12))

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.readlines()
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_repr(unittest.TestCase):
    def test(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual("riff.ChunkData(size=8)", repr(data))


class Test_ChunkData_seek(unittest.TestCase):
    def test_seeks_relative_to_start_by_default(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(4)
        self.assertEqual(4, data.tell())

    def test_seek_relative_to_start(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(4, io.SEEK_SET)
        self.assertEqual(4, data.tell())

    def test_seek_relative_to_start_constrained_by_start(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(-1, io.SEEK_SET)
        self.assertEqual(0, data.tell())

    def test_seek_relative_to_start_constrained_by_end(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(9, io.SEEK_SET)
        self.assertEqual(8, data.tell())

    def test_positive_seek_relative_to_current(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(1)
        data.seek(4, io.SEEK_CUR)
        self.assertEqual(5, data.tell())

    def test_negative_seek_relative_to_current(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(5)
        data.seek(-4, io.SEEK_CUR)
        self.assertEqual(1, data.tell())

    def test_seek_relative_to_current_constrained_by_start(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(4)
        data.seek(-5, io.SEEK_CUR)
        self.assertEqual(0, data.tell())

    def test_seek_relative_to_current_constrained_by_end(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(4)
        data.seek(5, io.SEEK_CUR)
        self.assertEqual(8, data.tell())

    def test_seek_relative_to_end(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(-4, io.SEEK_END)
        self.assertEqual(4, data.tell())

    def test_seek_relative_to_end_constrained_by_start(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(-9, io.SEEK_END)
        self.assertEqual(0, data.tell())

    def test_seek_relative_to_end_constrained_by_end(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(1, io.SEEK_END)
        self.assertEqual(8, data.tell())

    def test_ValueError_for_invalid_whence(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        with self.assertRaises(ValueError) as ctx:
            data.seek(4, whence=3)
        self.assertEqual('invalid whence value', str(ctx.exception))

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.seek(4)
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_seekable(unittest.TestCase):
    def test_returns_whether_stream_seekable(self):
        stream = io.BytesIO(b'SomeMockTestData')
        mock = unittest.mock.Mock()
        stream.seekable = unittest.mock.Mock(return_value=mock)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(mock, data.seekable())

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seekable = unittest.mock.Mock()
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.seekable()
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_size(unittest.TestCase):
    def test_returns_input_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(8, data.size)


class Test_ChunkData_streamfrom(unittest.TestCase):
    def test_closed_when_stream_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        stream.close()
        self.assertTrue(data.closed)

    def test_reads_from_start_position(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(b'Mock', data.read(4))

    def test_advances_stream_cursor_by_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(12, stream.tell())

    def test_not_closed_after_init(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertFalse(data.closed)

    def test_size_property_matches_input_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(8, data.size)


class Test_ChunkData_tell(unittest.TestCase):
    def test_returns_zero_after_init(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertEqual(0, data.tell())

    def test_returns_same_position_despite_stream_seek(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.seek(4, io.SEEK_SET)
        position_before = data.tell()
        stream.seek(10, io.SEEK_SET)
        self.assertEqual(position_before, data.tell())

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.tell()
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_truncate(unittest.TestCase):
    def test_raises_error_for_default_size(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        with self.assertRaises(io.UnsupportedOperation) as ctx:
            data.truncate()
        self.assertEqual('stream not writable', str(ctx.exception))

    def test_raises_error_when_size_specified(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        with self.assertRaises(io.UnsupportedOperation) as ctx:
            data.truncate(4)
        self.assertEqual('stream not writable', str(ctx.exception))

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.truncate()
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_writable(unittest.TestCase):
    def test_returns_False_despite_writable_stream(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.writable = unittest.mock.Mock(return_value=True)
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        self.assertFalse(data.writable())

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.writable()
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_writelines(unittest.TestCase):
    def test_raises_error(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        with self.assertRaises(io.UnsupportedOperation) as ctx:
            data.writelines([b'Line1\n', b'Line2\n'])
        self.assertEqual('stream not writable', str(ctx.exception))

    def test_does_not_call_stream_writelines_method(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.writelines = unittest.mock.Mock()
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        try:
            data.writelines([b'Line1\n', b'Line2\n'])
        except io.UnsupportedOperation:
            pass
        stream.writelines.assert_not_called()

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.writelines([b'Line1\n', b'Line2\n'])
        self.assertEqual('stream closed', str(ctx.exception))


class Test_ChunkData_write(unittest.TestCase):
    def test_raises_error(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        with self.assertRaises(io.UnsupportedOperation) as ctx:
            data.write(b'Data')
        self.assertEqual('stream not writable', str(ctx.exception))

    def test_does_not_call_stream_write_method(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.write = unittest.mock.Mock()
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        try:
            data.write(b'Data')
        except io.UnsupportedOperation:
            pass
        stream.write.assert_not_called()

    def test_ValueError_if_closed(self):
        stream = io.BytesIO(b'SomeMockTestData')
        stream.seek(4)
        data = riff.ChunkData.streamfrom(stream, size=8)
        data.close()
        with self.assertRaises(ValueError) as ctx:
            data.write(b'Data')
        self.assertEqual('stream closed', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
