from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict] = {}
        self.connection_count = 0

    async def connect(self, websocket: WebSocket, client_id: int, username: str) -> int:
        await websocket.accept()
        self.active_connections[client_id] = {
            "websocket": websocket,
            "username": username
        }
        self.connection_count += 1
        return client_id

    def disconnect(self, client_id: int):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            self.connection_count -= 1

    async def broadcast(self, message: str, exclude_client_id: int = None):
        """Broadcast a message to all connected clients, optionally excluding one"""
        disconnected_clients = []
        
        for client_id, connection_data in self.active_connections.items():
            if exclude_client_id is not None and client_id == exclude_client_id:
                continue
            try:
                await connection_data["websocket"].send_text(message)
            except:
                disconnected_clients.append(client_id)
        
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def send_personal_message(self, message: str, client_id: int):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id]["websocket"].send_text(message)
                return True
            except:
                self.disconnect(client_id)
        return False
    
    def get_connected_clients(self) -> List[int]:
        return list(self.active_connections.keys())
    
    def get_connected_users(self) -> List[Dict]:
        return [
            {"id": client_id, "username": data["username"]}
            for client_id, data in self.active_connections.items()
        ]
    
    def get_connection_count(self) -> int:
        return self.connection_count

manager = ConnectionManager()

async def chat_websocket_endpoint(websocket: WebSocket, client_id: int, username: str):
    await manager.connect(websocket, client_id, username)
    
    # Notify others that user joined
    await manager.broadcast(json.dumps({
        "type": "user_joined",
        "user_id": client_id,
        "username": username,
        "timestamp": datetime.now().isoformat(),
        "message": f"{username} a rejoint le chat"
    }))
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Broadcast the message to all clients
            await manager.broadcast(json.dumps({
                "type": "message",
                "user_id": client_id,
                "username": username,
                "message": data,
                "timestamp": datetime.now().isoformat()
            }))
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(json.dumps({
            "type": "user_left",
            "user_id": client_id,
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "message": f"{username} a quitté le chat"
        }))