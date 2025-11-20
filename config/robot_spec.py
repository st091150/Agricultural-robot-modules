from schemas.specification import RobotSpecification
from sensors.sensors import Camera, GPS_RTK, Mod
from schemas.specification import RobotData

ROBOT_SPEC = RobotSpecification(items=[Mod.specification, GPS_RTK.specification])

ROBOT_DATA = RobotData(
    items=[
        Mod(input_1=1, input_2=2, input_3=3),
        GPS_RTK(latitude=4, longitude=5),
    ]
)
