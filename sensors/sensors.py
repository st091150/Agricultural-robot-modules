from dataclasses import dataclass
from typing import ClassVar
from schemas.specification import SensorSpecification, SpecData, SpecDataTypeEnum


class BaseSensor:
    specification = None

    def __init_subclass__(cls):
        if cls.specification is None:
            raise TypeError(f"{cls.__name__} должен определить specification")


@dataclass
class Camera(BaseSensor):
    image: str

    specification: ClassVar[SensorSpecification] = SensorSpecification(
        name="Camera",
        model="Camera",
        data=[
            SpecData(description="img", data_type=SpecDataTypeEnum.STR, data_count=32)
        ],
    )


@dataclass
class Mod(BaseSensor):
    input_1: int
    input_2: int
    input_3: int

    specification: ClassVar[SensorSpecification] = SensorSpecification(
        name="Module",
        model="Module",
        data=[
            SpecData("input_1", SpecDataTypeEnum.INT, 4),
            SpecData("input_2", SpecDataTypeEnum.INT, 4),
            SpecData("input_2", SpecDataTypeEnum.INT, 4),
        ],
    )


@dataclass
class GPS_RTK(BaseSensor):
    latitude: int
    longitude: int

    specification: ClassVar[SensorSpecification] = SensorSpecification(
        name="GPS_RTK",
        model="GPS",
        data=[
            SpecData("latitude", SpecDataTypeEnum.INT, 4),
            SpecData("longitude", SpecDataTypeEnum.INT, 4),
        ],
    )
