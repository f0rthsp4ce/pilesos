from logging import getLogger
from os import getenv
from typing import Annotated

import serial
from pydantic import BaseModel, Field

logger = getLogger(__name__)

chassis_serial = serial.Serial(
    port=getenv("CHASSIS_PORT"), baudrate=115200, timeout=0.1
)


class Wheels(BaseModel):
    left: Annotated[int, Field(strict=True, ge=-255, le=255)]
    right: Annotated[int, Field(strict=True, ge=-255, le=255)]


class Lights(BaseModel):
    front_strip: tuple[int, int, int]


class Input(BaseModel):
    wheels: Wheels | None = None
    lights: Lights | None = None


def send_to_hardware(input: Input):
    s = input.model_dump_json(exclude_unset=True, exclude_none=True) + "\n"
    chassis_serial.write(s.encode())


def get_telemetry() -> str:
    return chassis_serial.readline().decode()
