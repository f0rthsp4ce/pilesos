from decimal import Decimal
from typing import Annotated
from pydantic import BaseModel, Field

from pilesos.hardware.battery import get_battery
from pilesos.hardware.bumper import left_bumper, right_bumper


class WebsocketTelemetry(BaseModel):
    battery_percent: int
    battery_volts: Annotated[Decimal, Field(decimal_places=1)]
    bumper_left: bool
    bumper_right: bool


def get_telemetry() -> WebsocketTelemetry:
    bat = get_battery()
    return WebsocketTelemetry(
        battery_percent=bat.percent,
        battery_volts=bat.volts,
        bumper_left=left_bumper.collision_detected,
        bumper_right=right_bumper.collision_detected,
    )
