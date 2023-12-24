import random

from pydantic import BaseModel

from pilesos.hardware.bumper import left_bumper, right_bumper


class WebsocketTelemetry(BaseModel):
    battery_percentage: int
    bumper_left: bool
    bumper_right: bool


def get_telemetry() -> WebsocketTelemetry:
    return WebsocketTelemetry(
        battery_percentage=random.randint(0, 100),
        bumper_left=left_bumper.collision_detected,
        bumper_right=right_bumper.collision_detected,
    )
