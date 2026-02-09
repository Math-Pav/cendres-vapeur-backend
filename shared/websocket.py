from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict



class ConnectionManager:
    def __init__(self):
        # Dictionnaire des connexions actives avec leurs métadonnées
        self.active_connections: Dict[int, WebSocket] = {}
        self.connection_count = 0

    async def connect(self, websocket: WebSocket, client_id: int) -> int:
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_count += 1
        return client_id

    def disconnect(self, client_id: int):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            self.connection_count -= 1

    async def broadcast(self, message: str, exclude_client_id: int = None):
        # Envoi instantané à tous les membres du secteur
        disconnected_clients = []
        for client_id, connection in self.active_connections.items():
            if exclude_client_id and client_id == exclude_client_id:
                continue
            try:
                await connection.send_text(message)
            except:
                # Marquer les connexions déconnectées pour nettoyage
                disconnected_clients.append(client_id)
        
        # Nettoyer les connexions déconnectées
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def send_personal_message(self, message: str, client_id: int):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
                return True
            except:
                self.disconnect(client_id)
        return False
    
    def get_connected_clients(self) -> List[int]:
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        return self.connection_count

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
    await manager.broadcast(f"Citoyen {client_id} a rejoint le canal.")
    
    try:
        while True:
            data = await websocket.receive_text()
            # Formatage immersif pour le Journal des survivants
            message_format = f"Citoyen {client_id} : {data}"
            await manager.broadcast(message_format, exclude_client_id=client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"Le citoyen {client_id} a quitté le canal.")