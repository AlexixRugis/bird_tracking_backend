import unittest
from tests.message_generator import MessageGenerator
from app.adapters.binary_protocol import BinaryProtocolParser

class TestBinaryProtocolParser(unittest.TestCase):
    def test_raise_on_none(self):
        parser = BinaryProtocolParser()
        
        with self.assertRaises(TypeError):
            parser.parse_packet(None)
            
    def test_raise_on_no_header(self):
        
        parser = BinaryProtocolParser()
        message_generator = MessageGenerator()
        message_generator.with_zeroes(2)
        
        with self.assertRaises(ValueError):
            parser.parse_packet(message_generator.get_buffer())
            
    def test_raise_on_short_msg(self):
        
        parser = BinaryProtocolParser()
        message_generator = MessageGenerator()
        message_generator.with_header(bytes("FFFFFFFFFFFF", "ascii"), 12)
        
        with self.assertRaises(ValueError):
            parser.parse_packet(message_generator.get_buffer())
    
    def test_raise_on_unknown_record_type(self):
        
        parser = BinaryProtocolParser()
        message_generator = MessageGenerator()
        
        message_generator.with_header(bytes("FFFFFFFFFFFF", "ascii"), 4)
        message_generator.with_bytes(bytes([10, 0, 0, 2]))
        
        with self.assertRaises(ValueError):
            parser.parse_packet(message_generator.get_buffer())
        
    
    def test_raise_on_incomplete_record(self):
        
        parser = BinaryProtocolParser()
        message_generator = MessageGenerator()
        
        message_generator.with_header(bytes("FFFFFFFFFFFF", "ascii"), 4)
        message_generator.with_bytes(bytes([0x02, 0, 0, 2]))
        
        with self.assertRaises(ValueError):
            parser.parse_packet(message_generator.get_buffer())
    
    def test_raise_on_invalid_crc(self):
        parser = BinaryProtocolParser()
        message_generator = MessageGenerator()
        
        message_generator.with_header(bytes("FFFFFFFFFFFF", "ascii"), 40)
        message_generator.with_message_0x02(12, 12.2, 22.5, [12, 12, 12],
                                            [34, 34, 43], [45, 64, 32],
                                            1.0, 30.0)
        message_generator.with_shrink_bytes(1)
        message_generator.with_bytes(bytes([0,]))
        
        with self.assertRaises(ValueError):
            parser.parse_packet(message_generator.get_buffer())
    
    def test_no_raise_on_empty_packet(self):
        
        parser = BinaryProtocolParser()
        message_generator = MessageGenerator()
        message_generator.with_header(bytes("FFFFFFFFFFFF", "ascii"), 0)
        
        result = parser.parse_packet(message_generator.get_buffer())
        self.assertEqual(len(result["messages"]), 0)
    
    def test_can_parse_device_id(self):
        
        parser = BinaryProtocolParser()
        message_generator = MessageGenerator()
        message_generator.with_header(bytes("quantum beer", "ascii"), 0)
        
        result = parser.parse_packet(message_generator.get_buffer())
        self.assertEqual(result["device_id"], bytes("quantum beer", "ascii").hex())
    
    def test_can_parse_type_0x02(self):
        
        msg = {
            'timestamp': 12, 
            'latitude': 12.2, 
            'longitude': 22.5, 
            'accelerometer': {'x': 12, 'y': 12, 'z': 12}, 
            'gyroscope': {'x': 34, 'y': 34, 'z': 43}, 
            'magnetometer': {'x': 45, 'y': 64, 'z': 32}, 
            'light': 1.0, 
            'temperature': 30.0
        }
        
        parser = BinaryProtocolParser()
        message_generator = MessageGenerator()
        
        message_generator.with_header(bytes("FFFFFFFFFFFF", "ascii"), 40)
        message_generator.with_message_0x02(
            msg['timestamp'], msg['latitude'], msg['longitude'], 
            [msg['accelerometer']['x'], msg['accelerometer']['y'], msg['accelerometer']['z']],
            [msg['gyroscope']['x'], msg['gyroscope']['y'], msg['gyroscope']['z']],
            [msg['magnetometer']['x'], msg['magnetometer']['y'], msg['magnetometer']['z']],
            msg['light'], msg['temperature'])
        
        result = parser.parse_packet(message_generator.get_buffer())
        
        # TODO: fix floats
        
        self.assertEqual(len(result['messages']), 1)
        self.assertEqual(result['messages'][0], msg)
    
    def test_break_on_0xFF(self):
        
        msg = {
            'timestamp': 12, 
            'latitude': 12.2, 
            'longitude': 22.5, 
            'accelerometer': {'x': 12, 'y': 12, 'z': 12}, 
            'gyroscope': {'x': 34, 'y': 34, 'z': 43}, 
            'magnetometer': {'x': 45, 'y': 64, 'z': 32}, 
            'light': 1.0, 
            'temperature': 30.0
        }
        
        parser = BinaryProtocolParser()
        message_generator = MessageGenerator()
        
        message_generator.with_header(bytes("FFFFFFFFFFFF", "ascii"), 81)
        message_generator.with_message_0x02(
            msg['timestamp'], msg['latitude'], msg['longitude'], 
            [msg['accelerometer']['x'], msg['accelerometer']['y'], msg['accelerometer']['z']],
            [msg['gyroscope']['x'], msg['gyroscope']['y'], msg['gyroscope']['z']],
            [msg['magnetometer']['x'], msg['magnetometer']['y'], msg['magnetometer']['z']],
            msg['light'], msg['temperature'])
        message_generator.with_bytes(bytes([0xFF,]))
        message_generator.with_message_0x02(
            msg['timestamp'], msg['latitude'], msg['longitude'], 
            [msg['accelerometer']['x'], msg['accelerometer']['y'], msg['accelerometer']['z']],
            [msg['gyroscope']['x'], msg['gyroscope']['y'], msg['gyroscope']['z']],
            [msg['magnetometer']['x'], msg['magnetometer']['y'], msg['magnetometer']['z']],
            msg['light'], msg['temperature'])
        
        result = parser.parse_packet(message_generator.get_buffer())
        
        self.assertEqual(len(result['messages']), 1)
    
    def test_can_parse_multiple_records(self):
        
        msg_1 = {
            'timestamp': 12, 
            'latitude': 12.2, 
            'longitude': 22.5, 
            'accelerometer': {'x': 12, 'y': 12, 'z': 12}, 
            'gyroscope': {'x': 34, 'y': 34, 'z': 43}, 
            'magnetometer': {'x': 45, 'y': 64, 'z': 32}, 
            'light': 1.0, 
            'temperature': 30.0
        }
        
        msg_2 = {
            'timestamp': 53, 
            'latitude': 13.5, 
            'longitude': 54.03, 
            'accelerometer': {'x': 234, 'y': -1232, 'z': 153}, 
            'gyroscope': {'x': 665, 'y': 0, 'z': 4124}, 
            'magnetometer': {'x': 234, 'y': 543, 'z': 222}, 
            'light': 0.667, 
            'temperature': 22.5
        }
        
        parser = BinaryProtocolParser()
        message_generator = MessageGenerator()
        
        message_generator.with_header(bytes("FFFFFFFFFFFF", "ascii"), 81)
        message_generator.with_message_0x02(
            msg_1['timestamp'], msg_1['latitude'], msg_1['longitude'], 
            [msg_1['accelerometer']['x'], msg_1['accelerometer']['y'], msg_1['accelerometer']['z']],
            [msg_1['gyroscope']['x'], msg_1['gyroscope']['y'], msg_1['gyroscope']['z']],
            [msg_1['magnetometer']['x'], msg_1['magnetometer']['y'], msg_1['magnetometer']['z']],
            msg_1['light'], msg_1['temperature'])
        message_generator.with_bytes(bytes([0xFF,]))
        message_generator.with_message_0x02(
            msg_2['timestamp'], msg_2['latitude'], msg_2['longitude'], 
            [msg_2['accelerometer']['x'], msg_2['accelerometer']['y'], msg_2['accelerometer']['z']],
            [msg_2['gyroscope']['x'], msg_2['gyroscope']['y'], msg_2['gyroscope']['z']],
            [msg_2['magnetometer']['x'], msg_2['magnetometer']['y'], msg_2['magnetometer']['z']],
            msg_2['light'], msg_2['temperature'])
        
        result = parser.parse_packet(message_generator.get_buffer())
        
        self.assertEqual(len(result['messages']), 2)
        self.assertEqual(result['messages'][0], msg_1)
        self.assertEqual(result['messages'][1], msg_2)

if __name__ == '__main__':
    unittest.main()