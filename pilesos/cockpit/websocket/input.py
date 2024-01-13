from logging import getLogger
from random import choice, randint

from pydantic import BaseModel

from pilesos.hardware.strip import (
    RGBW,
    ColorWipeEffect,
    RainbowCycleEffect,
    StripEffect,
    bumper_strip,
)
from pilesos.hardware.wheels import left_wheel_controller, right_wheel_controller
from pilesos.hardware.camera import front_camera

logger = getLogger(__name__)


class Joystick(BaseModel):
    x: float
    y: float


class Switches(BaseModel):
    lights: bool


class Buttons(BaseModel):
    camera_fix: bool


class WebsocketInput(BaseModel):
    joystick: Joystick | None = None
    buttons: Buttons | None = None
    switches: Switches | None = None


def map_joystick_to_tracks(joystick_x, joystick_y) -> tuple[int, int]:
    """Convert (X, Y) from joystick to (L, R) throttles for each motor in two-track vehicle (tank, vacuum cleaner)"""
    # nipplejs inverts joystick Y
    joystick_y = -joystick_y
    # value ranges
    max_joystick_value = 50
    max_track_throttle = 100
    # Map joystick values to track throttles
    left_track_throttle = (
        max_track_throttle * (joystick_y + joystick_x) / max_joystick_value
    )
    right_track_throttle = (
        max_track_throttle * (joystick_y - joystick_x) / max_joystick_value
    )
    # Ensure throttles are within the valid range
    left_track_throttle = max(
        -max_track_throttle, min(max_track_throttle, left_track_throttle)
    )
    right_track_throttle = max(
        -max_track_throttle, min(max_track_throttle, right_track_throttle)
    )
    return int(left_track_throttle), int(right_track_throttle)


async def process_websocket_input(user_input: WebsocketInput):
    if user_input.joystick:
        L_throttle, R_throttle = map_joystick_to_tracks(
            user_input.joystick.x, user_input.joystick.y
        )
        left_wheel_controller.set_speed(L_throttle)
        right_wheel_controller.set_speed(R_throttle)
        logger.debug("L=%s R=%s" % (L_throttle, R_throttle))
    if user_input.switches:
        effect: StripEffect | None = None
        if user_input.switches.lights:
            effect = choice(
                (
                    ColorWipeEffect(
                        color=RGBW(
                            randint(0, 255),
                            randint(0, 255),
                            randint(0, 255),
                        )
                    ),
                    RainbowCycleEffect(iterations=5),
                )
            )
        else:
            effect = ColorWipeEffect(color=RGBW(0, 0, 0))
        await bumper_strip.set_effect(effect)
