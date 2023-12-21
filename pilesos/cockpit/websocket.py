import json
from logging import getLogger
from typing import Annotated

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from pilesos.hardware.wheels import wheels_controller

logger = getLogger(__name__)
router = APIRouter()


class UserInput(BaseModel):
    wheels_left_speed: Annotated[int, Field(ge=-100, le=100, default=0)]
    wheels_right_speed: Annotated[int, Field(ge=-100, le=100, default=0)]


@router.websocket("/input")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug("data=%s" % data)

            user_input = UserInput(**json.loads(data))
            logger.debug("user_input=%s" % user_input)

            wheels_controller.set_speed("L", user_input.wheels_left_speed)
            wheels_controller.set_speed("R", user_input.wheels_right_speed)

            await websocket.send_text("ok")
    except WebSocketDisconnect:
        pass
