from .robot_state import IMAGE_SIZE_BYTES


def get_spec():
    return [
        {
            "name": "gps",
            "model": "GPS-A1",
            "observations": [
                {"description": "latitude",  "datatype": "double", "bytes": 8},
                {"description": "longitude", "datatype": "double", "bytes": 8},
            ],
        },
        {
            "name": "orientation",
            "model": "ROT-1",
            "observations": [
                {"description": "rotation_angle", "datatype": "uint16", "bytes": 2},
            ],
        },
        {
            "name": "camera",
            "model": "CamX",
            "observations": [
                {"description": "image", "datatype": "str", "bytes": IMAGE_SIZE_BYTES},
            ],
        },
    ]

