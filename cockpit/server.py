import asyncio
import json
import logging
from datetime import datetime, timedelta
from logging import getLogger

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from cockpit import chassis

logger = getLogger(__name__)

fastapi_app = FastAPI()
templates = Jinja2Templates(directory="cockpit/templates")

# css, js, jpg files
fastapi_app.mount("/static", StaticFiles(directory="cockpit/static"))


# main page
@fastapi_app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.jinja2", dict(request=request))


# websocket listener
@fastapi_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # needed for input_reset_killswitch
    last_received_input: datetime | None = None

    async def input_reset_killswitch(ws=websocket):
        logger = logging.getLogger("input_reset_killswitch")
        while True:
            if last_received_input and (
                datetime.now() - last_received_input > timedelta(milliseconds=500)
            ):
                # if there is no input from the user for >=1 second, then turn off motors, buzzers, etc.
                # this prevents the robot from deadmoving into something when the signal is lost.
                chassis.send_to_hardware(
                    chassis.Input(wheels=chassis.Wheels(left=0, right=0))
                )
                logger.debug("no input, resetting.")
            await asyncio.sleep(1)

    async def send_telemetry(ws=websocket):
        while True:
            await websocket.send_text(chassis.get_telemetry())
            await asyncio.sleep(0.01)

    input_reset_killswitch_task = asyncio.create_task(input_reset_killswitch())
    send_telemetry_task = asyncio.create_task(send_telemetry())
    try:
        while True:
            # get json from the browser
            data = await websocket.receive_text()
            logger.debug(data)
            # parse and validate it
            input = chassis.Input(**json.loads(data))
            # update motors, buzzers, lights, etc
            chassis.send_to_hardware(input)
            # reset killswitch, input is received
            last_received_input = datetime.now()
    except WebSocketDisconnect:
        send_telemetry_task.cancel()
        input_reset_killswitch_task.cancel()
