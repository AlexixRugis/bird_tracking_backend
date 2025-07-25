import struct
from typing import List, Dict, Any
import crcmod


CRC32_FUNC = crcmod.mkCrcFun(0x104C11DB7, initCrc=0xFFFFFFFF, rev=False, xorOut=0x00000000)

def swap_bytes_endianness(data: bytes, word_size: int = 4) -> bytes:
    """
    Переводит little-endian в big-endian
    """

    swapped_words = []
    for i in range(0, len(data), word_size):
        chunk = data[i:i + word_size]
        swapped_words.append(chunk[::-1])
    
    return b''.join(swapped_words)

class BinaryProtocolParser:
    """
    Парсит заголовок и поток сообщений протокола, описанного в binary_protocol.md
    Поддерживается только тип 0x02 (SensorData_ALL).
    """

    HEADER_FMT = "<I12sH"          # checksum, device_id, msg_length
    HEADER_SIZE = struct.calcsize(HEADER_FMT)

    MSG_SENSOR_ALL_FMT = "<BIffhhhhhhhhhff"
    MSG_SENSOR_ALL_SIZE = struct.calcsize(MSG_SENSOR_ALL_FMT)

    def parse_packet(self, raw: bytes) -> Dict[str, Any]:
        if len(raw) < self.HEADER_SIZE:
            raise ValueError("Пакет короче заголовка")

        crc32, device_id, msg_len = struct.unpack(
            self.HEADER_FMT, raw[: self.HEADER_SIZE]
        )

        body = raw[self.HEADER_SIZE :]
        if len(body) != msg_len:
            raise ValueError("Неверная длина блока сообщений")

        if CRC32_FUNC(swap_bytes_endianness(body)) != crc32:
            raise ValueError("CRC32 mismatch")

        messages = self._decode_messages(body)

        return {"device_id": device_id.hex(), "messages": messages}

    # ------------------------------------------------------------------ #

    def _decode_messages(self, body: bytes) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        idx = 0

        while idx < len(body):
            msg_type = body[idx]
            if msg_type == 0xFF:
                break

            if msg_type != 0x02:
                raise ValueError(f"Неизвестный msg_type={msg_type}")

            if len(body) - idx < self.MSG_SENSOR_ALL_SIZE:
                raise ValueError("Сообщение 0x02 обрезано")

            unpacked = struct.unpack(
                self.MSG_SENSOR_ALL_FMT, body[idx : idx + self.MSG_SENSOR_ALL_SIZE]
            )
            (
                _,
                timestamp,
                lat,
                lon,
                acc_x,
                acc_y,
                acc_z,
                gyr_x,
                gyr_y,
                gyr_z,
                mag_x,
                mag_y,
                mag_z,
                light,
                temp,
            ) = unpacked

            result.append(
                {
                    "timestamp": timestamp,
                    "latitude": lat,
                    "longitude": lon,
                    "accelerometer": {"x": acc_x, "y": acc_y, "z": acc_z},
                    "gyroscope": {"x": gyr_x, "y": gyr_y, "z": gyr_z},
                    "magnetometer": {"x": mag_x, "y": mag_y, "z": mag_z},
                    "light": light,
                    "temperature": temp,
                }
            )
            idx += self.MSG_SENSOR_ALL_SIZE

        return result
