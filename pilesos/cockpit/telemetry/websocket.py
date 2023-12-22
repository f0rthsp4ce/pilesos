import random

from pydantic import BaseModel


class WebsocketTelemetry(BaseModel):
    battery_percentage: int
    bumper_left: bool
    bumper_right: bool


def get_telemetry() -> WebsocketTelemetry:
    return WebsocketTelemetry(
        battery_percentage=random.randint(0, 100),
        bumper_left=False,
        bumper_right=True,
    )
