from fastapi import WebSocket
from typing import Dict
import json
from . import config

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        self.active_connections[job_id] = websocket

    def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]

    async def send_update(self, job_id: str, message: dict):
        if job_id in self.active_connections:
            await self.active_connections[job_id].send_json(message)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect(websocket, job_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except Exception as e:
        manager.disconnect(job_id) 