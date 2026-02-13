from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel, EmailStr
from api import router
from shared.mailer import envoyer_missive
from shared.security import require_roles
from shared.websocket import manager

router = APIRouter(prefix="/mail", tags=["mail"])

class Missive(BaseModel):
    """
    Modèle de données pour la missive
    """
    expediteur: EmailStr
    sujet: str
    message: str


@router.post("/", dependencies=[Depends(require_roles("ADMIN", "EDITOR", "USER"))])
async def envoyer_une_missive(missive: Missive):
    """
    Envoie une missive au Grand Conseil via le tunnel sécurisé

    Roles allowed: ADMIN, EDITOR, USER
    """
    try:
        notification = f"📡 Missive transmise: {missive.sujet} de {missive.expediteur}"
        await manager.broadcast(notification)
        
        resultat = await envoyer_missive(missive)
        return resultat
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    client_id: int = Query(..., description="User ID"),
    username: str = Query(..., description="Username to display in chat")
):
    """
    WebSocket endpoint for real-time chat
    
    Connect with: ws://yourapi.com/mail/ws?client_id=123&username=YourName
    
    Message format received:
    {
        "type": "message" | "user_joined" | "user_left",
        "user_id": 123,
        "username": "YourName",
        "message": "Hello everyone!",
        "timestamp": "2026-02-12T10:30:00"
    }
    
    To send a message: just send plain text through the WebSocket
    """
    from shared.websocket import chat_websocket_endpoint
    await chat_websocket_endpoint(websocket, client_id, username)


@router.get("/users")
async def get_online_users():
    """
    Get list of currently connected users
    
    Returns: [{"id": 1, "username": "Alice"}, {"id": 2, "username": "Bob"}]
    """
    return {
        "online_users": manager.get_connected_users(),
        "count": manager.get_connection_count()
    }


class BroadcastMessage(BaseModel):
    message: str
    exclude_client_id: int = None


@router.post("/broadcast", dependencies=[Depends(require_roles("ADMIN", "EDITOR"))])
async def broadcast_message(message_data: BroadcastMessage):
    """
    Diffuser un message à tous les clients WebSocket connectés

        Roles allowed: ADMIN, EDITOR
    """
    await manager.broadcast(message_data.message, message_data.exclude_client_id)
    return {"status": "message_broadcasted", "message": message_data.message}


@router.post("/disconnect-client/{client_id}", dependencies=[Depends(require_roles("ADMIN", "EDITOR"))])
async def disconnect_client(client_id: int):
    """
    Déconnecter manuellement un client WebSocket

        Roles allowed: ADMIN, EDITOR
    """
    if client_id in manager.get_connected_clients():
        manager.disconnect(client_id)
        return {"status": "client_disconnected", "client_id": client_id}
    else:
        raise HTTPException(status_code=404, detail=f"Client {message_data.client_id} not connected")