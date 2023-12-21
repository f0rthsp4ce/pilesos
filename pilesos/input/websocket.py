from typing import Annotated

from pydantic import BaseModel, Field

from pilesos.hardware.wheels import wheels_controller


class WebsocketInput(BaseModel):
    wheels_left_speed: Annotated[int, Field(ge=-100, le=100, default=0)]
    wheels_right_speed: Annotated[int, Field(ge=-100, le=100, default=0)]


def process_websocket_input(user_input: WebsocketInput):
    wheels_controller.set_speed("L", user_input.wheels_left_speed)
    wheels_controller.set_speed("R", user_input.wheels_right_speed)
