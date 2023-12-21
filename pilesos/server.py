from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from pilesos.cockpit.endpoints import router as endpoints_router
from pilesos.cockpit.websocket import router as websocket_router

fastapi_app = FastAPI()
fastapi_app.mount("/static", StaticFiles(directory="pilesos/cockpit/static"))

fastapi_app.include_router(websocket_router)
fastapi_app.include_router(endpoints_router)
