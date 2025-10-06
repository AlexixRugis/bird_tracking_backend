import struct
from typing import Self, List
from crcmod.predefined import mkCrcFun

CRC8_FUNC = mkCrcFun('crc-8-maxim')

class MessageGenerator:
    __buffer: bytes
    
    def __init__(self):
        self.__buffer = bytes()
    
    def get_buffer(self) -> bytes:
        return self.__buffer
    
    def with_bytes(self, data: bytes) -> Self:
        self.__buffer += data
        
        return self
    
    def with_zeroes(self, zeroLength: int) -> Self:
        
        if zeroLength < 0:
            raise ValueError("zeroLength must be positive integer")
        
        self.__buffer += bytes(zeroLength)
        
        return self
    
    def with_header(self, id: bytes, packetLength: int) -> Self:
        
        if len(id) != 12:
            raise ValueError("id must be exactly 12 bytes len")
        if packetLength < 0:
            raise ValueError("packetLength must be positive integer")
        
        header = struct.pack("<12sH", id, packetLength)
        
        self.__buffer += header
        
        return self
    
    def with_message_0x02(self, timestamp: int, latitude: float, longitude: float,
                          acc: List[int], gyro: List[int], mag: List[int],
                          light: float, temp: float) -> Self:
        
        msg = struct.pack("<BIffhhhhhhhhhff", 0x02, timestamp, latitude,
                          longitude, acc[0], acc[1], acc[2],
                          gyro[0], gyro[1], gyro[2], mag[0], mag[1], mag[2],
                          light, temp)
        
        crc = CRC8_FUNC(msg)
        
        self.__buffer += msg
        self.__buffer += bytes([crc,])
        
        return self
    
    def with_shrink_bytes(self, count: int) -> Self:
        
        if count < 0:
            raise ValueError("count must be positive integer")
        if count > len(self.__buffer):
            raise ValueError("count must be not greater than buffer length")
        
        self.__buffer = self.__buffer[0:-count]
        
        return self
    