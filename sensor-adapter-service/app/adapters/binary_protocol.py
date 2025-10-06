import struct
from logging import getLogger
from typing import List, Dict, Any
from crcmod.predefined import mkCrcFun

logger = getLogger(__name__)
CRC8_FUNC = mkCrcFun('crc-8-maxim')

class BinaryProtocolParser:
    """
    Парсит заголовок и поток сообщений протокола, описанного в binary_protocol.md
    Поддерживается только тип 0x02 (SensorData_ALL).
    """

    HEADER_FMT = "<12sH"          # device_id, msg_length
    HEADER_SIZE = struct.calcsize(HEADER_FMT)
    
    CRC_FMT = "<B"
    CRC_SIZE = struct.calcsize(CRC_FMT)

    MSG_SENSOR_ALL_FMT = "<BIffhhhhhhhhhff"
    MSG_SENSOR_ALL_SIZE = struct.calcsize(MSG_SENSOR_ALL_FMT)

    def parse_packet(self, raw: bytes) -> Dict[str, Any]:
        if len(raw) < self.HEADER_SIZE:
            logger.error("The packet is shorter than the header")
            raise ValueError("Пакет короче заголовка")

        device_id, msg_len = struct.unpack(
            self.HEADER_FMT, raw[: self.HEADER_SIZE]
        )
        
        logger.info(f"Decoded device_id={device_id.hex()}, msg_len={msg_len}")

        body = raw[self.HEADER_SIZE :]
        if len(body) != msg_len:
            logger.error("Invalid message block length")
            raise ValueError("Неверная длина блока сообщений")

        messages = self._decode_messages(body)
        
        logger.info(f"Successfully decoded {len(messages)} messages")

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
                logger.error(f"Unknown msg_type={msg_type}")
                raise ValueError(f"Неизвестный msg_type={msg_type}")

            if len(body) - idx < self.MSG_SENSOR_ALL_SIZE + self.CRC_SIZE:
                logger.error("The message of type 0x02 is not full")
                raise ValueError("Сообщение 0x02 обрезано")

            unpacked = struct.unpack(
                self.MSG_SENSOR_ALL_FMT, body[idx : idx + self.MSG_SENSOR_ALL_SIZE]
            )
            
            (crc_8, ) = struct.unpack(
                self.CRC_FMT, body[idx + self.MSG_SENSOR_ALL_SIZE : idx + self.MSG_SENSOR_ALL_SIZE
                                   + self.CRC_SIZE]
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
            
            if not CRC8_FUNC(body[idx : idx + self.MSG_SENSOR_ALL_SIZE]) == crc_8:
                logger.error("The message has invalid crc8")
                raise ValueError("Неверная контрольная сумма сообщения")

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
            idx += self.MSG_SENSOR_ALL_SIZE + self.CRC_SIZE

        return result
