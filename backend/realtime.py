from typing import Dict, List, Any
import json
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class GroupConnectionManager:
    def __init__(self):
        # Maps group_id -> list of active WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, group_id: int, websocket: WebSocket):
        await websocket.accept()
        if group_id not in self.active_connections:
            self.active_connections[group_id] = []
        self.active_connections[group_id].append(websocket)
        logger.info(f"WebSocket connected for group {group_id}. Active: {len(self.active_connections[group_id])}")

    def disconnect(self, group_id: int, websocket: WebSocket):
        if group_id in self.active_connections:
            if websocket in self.active_connections[group_id]:
                self.active_connections[group_id].remove(websocket)
            if not self.active_connections[group_id]:
                del self.active_connections[group_id]
        logger.info(f"WebSocket disconnected for group {group_id}.")

    async def broadcast_to_group(self, group_id: int, message: Dict[str, Any]):
        if group_id in self.active_connections:
            stale_connections = []
            for connection in list(self.active_connections[group_id]):
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.warning(f"Failed sending WS message to group {group_id}: {e}")
                    stale_connections.append(connection)

            for stale in stale_connections:
                self.disconnect(group_id, stale)


manager = GroupConnectionManager()
