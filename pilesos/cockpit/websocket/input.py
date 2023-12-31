from logging import getLogger

from pydantic import BaseModel

from pilesos.hardware.wheels import left_wheel_controller, right_wheel_controller

logger = getLogger(__name__)


class Joystick(BaseModel):
    x: float
    y: float


class Switches(BaseModel):
    lights: bool


class Buttons(BaseModel):
    buzzer: bool


class WebsocketInput(BaseModel):
    joystick: Joystick | None
    buttons: Buttons | None
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


def process_websocket_input(user_input: WebsocketInput):
    if user_input.joystick:
        L_throttle, R_throttle = map_joystick_to_tracks(
            user_input.joystick.x, user_input.joystick.y
        )
        left_wheel_controller.set_speed(L_throttle)
        right_wheel_controller.set_speed(R_throttle)
        logger.debug("L=%s R=%s" % (L_throttle, R_throttle))
