from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from api import router
from shared.mailer import envoyer_missive

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
        resultat = await envoyer_missive(missive)
        return resultat
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


