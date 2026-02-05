import json
import bcrypt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from apps.models.customUser import CustomUser


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
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
    
    return JsonResponse({
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "biography": user.biography
        },
        "message": "Connexion réussie"
    }, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def register(request):
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
    users = CustomUser.objects.all().values()
    return JsonResponse({
        "success": True,
        "users": list(users)
    }, status=200)
