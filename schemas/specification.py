from typing import List
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel


class SpecDataTypeEnum(str, Enum):
    INT = "int"
    FLOAT = "float"
    DOUBLE = "double"
    BOOL = "bool"
    BYTES = "bytes"
    STR = "str"


@dataclass
class SpecData:
    description: str
    data_type: SpecDataTypeEnum
    data_count: int


@dataclass(frozen=True)
class SensorSpecification:
    name: str
    model: str
    data: List[SpecData]


@dataclass
class RobotData:
    items: List["BaseSensor"] = field(default_factory=list)

    def __post_init__(self):
        from sensors.sensors import BaseSensor  # импорт тут безопасен

        for i, sensor in enumerate(self.items):
            if not isinstance(sensor, BaseSensor):
                raise TypeError(
                    f"Элемент {i} ({sensor}) не является наследником BaseSensor"
                )

    def add_sensor(self, sensor: "BaseSensor"):
        from sensors.sensors import BaseSensor

        if not isinstance(sensor, BaseSensor):
            raise TypeError(
                f"{sensor.__class__.__name__} не является наследником BaseSensor"
            )
        self.items.append(sensor)


class RobotSpecification(BaseModel):
    items: List[SensorSpecification]
