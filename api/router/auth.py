import bcrypt
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from django.utils import timezone
from apps.classes.log import create_log
from apps.models.customUser import CustomUser
from apps.models.twoFactorCode import TwoFactorCode
from shared.security import generate_2fa_code, generate_jwt_token, require_roles
from shared.mailer import send_2fa_code_email, send_welcome_email


router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class Verify2FARequest(BaseModel):
    user_id: int
    code: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    avatar_url: str | None = None
    biography: str | None = None


@router.post("/login/")
def login(data: LoginRequest):
    """
    Étape 1 du login: Valider email/password
    Génère un code 2FA et l'envoie par email
    Retourne une session temporaire pour la prochaine étape
    """
    email = data.email.strip()
    password = data.password
    
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    two_fa_code = generate_2fa_code()
    
    TwoFactorCode.objects.filter(user=user).delete()
    
    expires_at = timezone.now() + timedelta(minutes=10)
    TwoFactorCode.objects.create(
        user=user,
        code=two_fa_code,
        expires_at=expires_at
    )
    
    send_2fa_code_email(user.email, two_fa_code, user.username)
    
    return {
        "success": True,
        "message": "Code 2FA envoyé par email",
        "user_id": user.id,
        "email": user.email,
        "next_step": "Validez le code 2FA",
        "expiry_minutes": 10
    }


@router.post("/verify-2fa/")
def verify_2fa(data: Verify2FARequest):
    """
    Étape 2 du login: Valider le code 2FA
    Génère et retourne un JWT token
    """
    user_id = data.user_id
    code = data.code.strip()
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    try:
        two_fa = TwoFactorCode.objects.get(user=user, code=code)
    except TwoFactorCode.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Code 2FA invalide"
        )
    
    if timezone.now() > two_fa.expires_at:
        two_fa.delete()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Code 2FA expiré"
        )
    
    create_log("2FA verified", user.username)
    token = generate_jwt_token(user)
    
    two_fa.delete()
    
    return {
        "success": True,
        "message": "Authentification réussie",
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "biography": user.biography
        },
        "expires_in": "24h"
    }


@router.post("/register/")
def register(data: RegisterRequest):
    """
    Inscription: Créer un nouvel utilisateur
    """
    username = data.username.strip()
    email = data.email.strip()
    password = data.password
    
    if CustomUser.objects.filter(email=email).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email existe déjà"
        )
    
    if CustomUser.objects.filter(username=username).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce username existe déjà"
        )
    
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    user = CustomUser.objects.create(
        username=username,
        email=email,
        password=hashed_password,
        role='USER'
    )
    create_log("Register event created", user)
    send_welcome_email(user.email, user.username)
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        },
        "message": "Utilisateur créé avec succès"
    }


@router.get("/users/", dependencies=[Depends(require_roles("ADMIN"))])
def users_list():
    """Liste tous les utilisateurs (test)"""
    users = CustomUser.objects.all().values()
    return {
        "success": True,
        "users": list(users)
    }

