import struct
import crcmod
from dataclasses import fields, is_dataclass
from typing import get_origin, get_args, List

# соответствие Python-типа — функции упаковки в бинарный вид
TYPE_MAP = {
    int: {"func": lambda v: struct.pack("<i", v), "byte_reverse": True},
    float: {"func": lambda v: struct.pack("<f", v), "byte_reverse": True},
    bool: {"func": lambda v: struct.pack("?", v), "byte_reverse": True},
    # str:   {"func": lambda v: v.encode("utf-8"), "byte_reverse": False},  # строки не переворачиваем
    bytes: {"func": lambda v: v, "byte_reverse": False},  # байты оставляем как есть
}


crc_func = crcmod.predefined.mkCrcFun("crc-32")


def bytes_to_bits(b: bytes) -> str:
    """Преобразует байты в строку из 0 и 1."""
    return "".join(f"{byte:08b}" for byte in b)


def to_binary(obj: object) -> bytes:
    """Конвертирует dataclass в бинарное представление, учитывая specification.data_count.
    Поля binary_data и crc_16 игнорируются."""

    if not is_dataclass(obj):
        raise TypeError(
            f"to_binary: объект должен быть dataclass, получено {type(obj)}"
        )

    binary = b""

    # Берём спецификацию, если есть
    spec_data = getattr(obj, "specification", None)
    spec_fields: List = getattr(spec_data, "data", []) if spec_data else []
    sd_idx = 0  # индекс по specification.data

    for f in fields(obj):
        if f.name in ("binary_data", "crc_16"):
            continue

        value = getattr(obj, f.name)

        # Если значение список
        if isinstance(value, list):
            for item in value:
                binary += to_binary(item)

        # Вложенный датакласс
        elif is_dataclass(value):
            binary += to_binary(value)

        # Примитивный тип
        elif type(value) in TYPE_MAP:
            conv_info = TYPE_MAP[type(value)]
            b = conv_info["func"](value)

            # Проверяем data_count из specification
            if sd_idx < len(spec_fields):
                data_count = spec_fields[sd_idx].data_count
                sd_idx += 1
                if data_count > len(b):
                    b = b"\x00" * (data_count - len(b)) + b  # нули слева

            # Переворачиваем порядок байт, если указано
            if conv_info.get("byte_reverse", False):
                b = b[::-1]

            binary += b

        else:
            raise TypeError(f"Тип поля {f.name} ({type(value)}) не поддержан")

    return binary
