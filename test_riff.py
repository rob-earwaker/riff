import io
import riff
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
        chunk = riff.Chunk.streamfrom(iostream)
        self.assertIsInstance(chunk.data, riff.ChunkData)


class Test_Chunk_id(unittest.TestCase):
    def test_value_after_creating_chunk(self):
        datastream = io.BytesIO(b'MockData')
        chunk = riff.Chunk.create('MOCK', 8, datastream)
        self.assertEqual('MOCK', chunk.id)

    def test_value_after_reading_chunk_from_stream(self):
        iostream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(iostream)
        self.assertEqual('MOCK', chunk.id)


class Test_Chunk_padded(unittest.TestCase):
    def test_True_if_size_odd_and_pad_byte_expected(self):
        iostream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(iostream)
        self.assertTrue(chunk.padded)

    def test_True_if_size_odd_and_pad_byte_not_expected(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        self.assertTrue(chunk.padded)

    def test_False_if_size_even_and_pad_byte_expected(self):
        iostream = io.BytesIO(b'MOCK\x08\x00\x00\x00MockData')
        chunk = riff.Chunk.streamfrom(iostream)
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
        riff.Chunk.streamfrom(iostream)

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
        chunk = riff.Chunk.streamfrom(iostream)
        self.assertEqual("riff.Chunk(id='MOCK', size=8)", repr(chunk))

    def test_for_padded_chunk_read_from_stream(self):
        iostream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(iostream)
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
        chunk = riff.Chunk.streamfrom(iostream)
        self.assertEqual(8, chunk.size)

    def test_value_after_creating_padded_chunk(self):
        datastream = io.BytesIO(b'MockDataOdd')
        chunk = riff.Chunk.create('MOCK', 11, datastream)
        self.assertEqual(11, chunk.size)

    def test_value_after_reading_padded_chunk_from_stream(self):
        iostream = io.BytesIO(b'MOCK\x0b\x00\x00\x00MockDataOdd\x00')
        chunk = riff.Chunk.streamfrom(iostream)
        self.assertEqual(11, chunk.size)


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


class Test_RiffChunk_readfrom(unittest.TestCase):
    def test_error_for_non_riff_id(self):
        iostream = io.BytesIO(b'MOCK\x04\x00\x00\x00TEST')
        with self.assertRaises(riff.Error) as ctx:
            riff.RiffChunk.readfrom(iostream)
        self.assertEqual("unexpected chunk id 'MOCK'", str(ctx.exception))

    def test_error_for_truncated_chunk_format(self):
        iostream = io.BytesIO(b'RIFF\x02\x00\x00\x00MO')
        with self.assertRaises(riff.Error) as ctx:
            riff.RiffChunk.readfrom(iostream)
        self.assertEqual('riff chunk format truncated', str(ctx.exception))

    def test_error_for_invalid_chunk_format(self):
        iostream = io.BytesIO(b'RIFF\x04\x00\x00\x00MO\xffK')
        with self.assertRaises(riff.Error) as ctx:
            riff.RiffChunk.readfrom(iostream)
        expected_message = 'riff chunk format not ascii-decodable'
        self.assertEqual(expected_message, str(ctx.exception))


class Test_RiffChunk_subchunks(unittest.TestCase):
    def test_can_iterate_subchunks(self):
        iostream = io.BytesIO(
            b'RIFF\x1c\x00\x00\x00MOCK' +
            b'CNKA\x04\x00\x00\x00AAAA' +
            b'CNKB\x04\x00\x00\x00BBBB'
        )
        riffchunk = riff.RiffChunk.readfrom(iostream)
        for subchunk in riffchunk.subchunks():
            self.assertIsInstance(subchunk, riff.Chunk)


if __name__ == '__main__':
    unittest.main()
