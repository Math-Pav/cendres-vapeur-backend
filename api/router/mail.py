from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, EmailStr
from api import router
from shared.mailer import envoyer_missive
from shared.websocket import manager

router = APIRouter(prefix="/mail", tags=["mail"])


class Missive(BaseModel):
    """
    Modèle de données pour la missive
    """
    expediteur: EmailStr
    sujet: str
    message: str


@router.post("/")
async def envoyer_une_missive(missive: Missive):
    """
    Envoie une missive au Grand Conseil via le tunnel sécurisé
    """
    try:
        # Notifier tous les clients connectés qu'une missive a été envoyée
        notification = f"📡 Missive transmise: {missive.sujet} de {missive.expediteur}"
        await manager.broadcast(notification)
        
        resultat = await envoyer_missive(missive)
        return resultat
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    """
    Endpoint WebSocket pour la communication en temps réel du secteur
    """
    from shared.websocket import websocket_endpoint as ws_handler
    await ws_handler(websocket, client_id)


@router.get("/status")
async def get_status():
    """
    Statut des connexions WebSocket actives
    """
    return {
        "connected_clients": manager.get_connected_clients(),
        "connection_count": manager.get_connection_count()
    }


