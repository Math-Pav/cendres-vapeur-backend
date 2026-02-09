from fastapi import Depends, HTTPException, status, Header
import jwt
import random
import string
from datetime import datetime, timedelta
from django.conf import settings


def generate_2fa_code():
    """Génère un code numérique aléatoire de 6 chiffres"""
    return ''.join(random.choices(string.digits, k=6))


def generate_jwt_token(user):
    """
    Génère un JWT token pour l'utilisateur
    Token expire après 24h
    """
    payload = {
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def verify_jwt_token(token):
    """
    Vérifie et décode un JWT token
    Retourne le payload si valide, None sinon
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  
    except jwt.InvalidTokenError:
        return None 


def get_current_payload(authorization: str = Header(...)):
    """
    Dépendance FastAPI pour extraire et vérifier le JWT token
    Retourne le payload du token ou lève une exception si invalide
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    payload = verify_jwt_token(token)
    
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    return payload
    

def require_roles(*roles):
    def _checker(payload = Depends(get_current_payload)):
        if payload.get("role") not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return payload
    return _checker