import json
from logging import getLogger

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pilesos.cockpit.websocket.input import (WebsocketInput,
                                             process_websocket_input)
from pilesos.cockpit.websocket.telemetry import get_telemetry

logger = getLogger(__name__)

fastapi_app = FastAPI()
templates = Jinja2Templates(directory="pilesos/cockpit/templates")

# css, js, jpg files
fastapi_app.mount("/static", StaticFiles(directory="pilesos/cockpit/static"))


# main page
@fastapi_app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.jinja2", dict(request=request))


# websocket listener
@fastapi_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(data)
            user_input = WebsocketInput(**json.loads(data))
            process_websocket_input(user_input)
            await websocket.send_text(get_telemetry().model_dump_json())
    except WebSocketDisconnect:
        pass
