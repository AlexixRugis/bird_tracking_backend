import unittest
from app.adapters.binary_protocol import BinaryProtocolParser

class TestBinaryProtocolParser(unittest.TestCase):
    def test_raise_on_none(self):
        parser = BinaryProtocolParser()
        
        with self.assertRaises(TypeError):
            parser.parse_packet(None)
            
    def test_raise_on_short_msg(self):
        pass
    
    def test_raise_on_too_big_msg(self):
        pass
    
    def test_raise_on_incorrect_msg_size(self):
        pass
    
    def test_raise_on_unknown_record_type(self):
        pass
    
    def test_raise_on_incomplete_record(self):
        pass
    
    def test_raise_on_invalid_crc(self):
        pass
    
    def test_can_parse_device_id(self):
        pass
    
    def test_can_parse_type_0x02(self):
        pass
    
    def test_can_parse_multiple_record(self):
        pass

if __name__ == '__main__':
    unittest.main()