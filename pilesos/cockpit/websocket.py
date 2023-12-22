import json
from logging import getLogger

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from pilesos.cockpit.input.websocket import WebsocketInput, process_websocket_input

logger = getLogger(__name__)
router = APIRouter()


@router.websocket("/input")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            user_input = WebsocketInput(**json.loads(data))
            process_websocket_input(user_input)
            await websocket.send_text("ok")
    except WebSocketDisconnect:
        pass
