import json
import bcrypt
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from apps.models.customUser import CustomUser
from apps.models.twoFactorCode import TwoFactorCode
from shared.security import generate_2fa_code, generate_jwt_token
from shared.mailer import send_2fa_code_email, send_welcome_email


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """
    Étape 1 du login: Valider email/password
    Génère un code 2FA et l'envoie par email
    Retourne une session temporaire pour la prochaine étape
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "JSON invalide"
        }, status=400)
    
    email = data.get("email", "").strip()
    password = data.get("password", "")
    
    if not email or not password:
        return JsonResponse({
            "success": False,
            "error": "Email et mot de passe requis"
        }, status=400)
    
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Email ou mot de passe incorrect"
        }, status=401)
    
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        return JsonResponse({
            "success": False,
            "error": "Email ou mot de passe incorrect"
        }, status=401)
    
    two_fa_code = generate_2fa_code()
    
    TwoFactorCode.objects.filter(user=user).delete()
    
    expires_at = timezone.now() + timedelta(minutes=10)
    TwoFactorCode.objects.create(
        user=user,
        code=two_fa_code,
        expires_at=expires_at
    )
    
    send_2fa_code_email(user.email, two_fa_code, user.username)
    
    return JsonResponse({
        "success": True,
        "message": "Code 2FA envoyé par email",
        "user_id": user.id,
        "email": user.email,
        "next_step": "Validez le code 2FA",
        "expiry_minutes": 10
    }, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def verify_2fa(request):
    """
    Étape 2 du login: Valider le code 2FA
    Génère et retourne un JWT token
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "JSON invalide"
        }, status=400)
    
    user_id = data.get("user_id")
    code = data.get("code", "").strip()
    
    if not user_id or not code:
        return JsonResponse({
            "success": False,
            "error": "user_id et code requis"
        }, status=400)
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Utilisateur non trouvé"
        }, status=404)
    
    try:
        two_fa = TwoFactorCode.objects.get(user=user, code=code)
    except TwoFactorCode.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Code 2FA invalide"
        }, status=401)
    
    if timezone.now() > two_fa.expires_at:
        two_fa.delete()
        return JsonResponse({
            "success": False,
            "error": "Code 2FA expiré"
        }, status=401)
    
    token = generate_jwt_token(user)
    
    two_fa.delete()
    
    return JsonResponse({
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
    }, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    """
    Inscription: Créer un nouvel utilisateur
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "JSON invalide"
        }, status=400)
    
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    
    if not username or not email or not password:
        return JsonResponse({
            "success": False,
            "error": "Username, email et password requis"
        }, status=400)
    
    if CustomUser.objects.filter(email=email).exists():
        return JsonResponse({
            "success": False,
            "error": "Cet email existe déjà"
        }, status=400)
    
    if CustomUser.objects.filter(username=username).exists():
        return JsonResponse({
            "success": False,
            "error": "Ce username existe déjà"
        }, status=400)
    
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    user = CustomUser.objects.create(
        username=username,
        email=email,
        password=hashed_password,
        role='USER'
    )
    
    send_welcome_email(user.email, user.username)
    
    return JsonResponse({
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        },
        "message": "Utilisateur créé avec succès"
    }, status=201)


@csrf_exempt
@require_http_methods(["GET"])
def users_list(request):
    """Liste tous les utilisateurs (test)"""
    users = CustomUser.objects.all().values()
    return JsonResponse({
        "success": True,
        "users": list(users)
    }, status=200)
