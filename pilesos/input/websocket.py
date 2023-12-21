from typing import Annotated

from pydantic import BaseModel, Field

from pilesos.hardware.wheels import wheels_controller


class WheelsJoystick(BaseModel):
    x: Annotated[int, Field(ge=-100, le=100, default=0)]
    y: Annotated[int, Field(ge=-100, le=100, default=0)]
    leveledX: Annotated[int, Field(ge=-10, le=10, default=0)]
    leveledY: Annotated[int, Field(ge=-10, le=10, default=0)]
    distance: float
    angle: float


class WebsocketInput(BaseModel):
    wheels_joystick: WheelsJoystick


def process_websocket_input(user_input: WebsocketInput):
    wheels_controller.set_speed("L", user_input.wheels_joystick.x)
    wheels_controller.set_speed("R", user_input.wheels_joystick.y)
