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
