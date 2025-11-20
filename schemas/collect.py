from pydantic import BaseModel
from dataclasses import dataclass, field
from utils import crc_func, to_binary, bytes_to_bits
from schemas.specification import RobotData


@dataclass
class CollectResponse:
    data: RobotData
    # Помечаем данные "exclude", чтоб не учитывать их в to_binary
    bytes_data: bytes = field(init=False, default=b"", metadata={"exclude": True})
    binary_data: bytes = field(init=False, default=b"", metadata={"exclude": True})
    crc_16: bytes = field(init=False, default=0, metadata={"exclude": True})

    # post_init для автоматического вычисления crc_16 и binary_data
    def __post_init__(self):
        self.bytes_data = to_binary(self)
        self.binary_data = bytes_to_bits(self.bytes_data)
        self.crc_16 = crc_func(self.bytes_data)
