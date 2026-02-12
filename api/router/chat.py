from fastapi import APIRouter, WebSocket, Query
from shared.websocket import manager, chat_websocket_endpoint

router = APIRouter(prefix="/chat", tags=["chat"])


@router.websocket("/ws")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    client_id: int = Query(..., description="User ID"),
    username: str = Query(..., description="Username to display in chat")
):
    """
    WebSocket endpoint for real-time chat
    
    Connect with: ws://yourapi.com/chat/ws?client_id=123&username=YourName
    
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
