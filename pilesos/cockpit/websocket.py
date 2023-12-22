import json
from logging import getLogger

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from pilesos.cockpit.input.websocket import WebsocketInput, process_websocket_input
from pilesos.cockpit.telemetry.websocket import get_telemetry

logger = getLogger(__name__)
router = APIRouter()


@router.websocket("/input")
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
