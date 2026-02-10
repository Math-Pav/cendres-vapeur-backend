from apps.models import CustomUser
from django.contrib.auth.hashers import make_password
from apps.classes.log import create_log
from apps.classes.log import create_log

def list_users():
    return CustomUser.objects.all()

def list_users_advanced(search: str = None, role: str = None, page: int = 1, limit: int = 20):
    """
    Liste les utilisateurs avec filtres, recherche et pagination
    
    Args:
        search: Recherche par username ou email
        role: Filtrer par rôle (ADMIN, EDITOR, USER, INVITE)
        page: Numéro de page (default: 1)
        limit: Nombre de résultats par page (default: 20, max: 100)
    """
    query = CustomUser.objects.all()
    
    if role and role.upper() in ['ADMIN', 'EDITOR', 'USER', 'INVITE']:
        query = query.filter(role=role.upper())
    
    if search:
        from django.db.models import Q
        query = query.filter(Q(username__icontains=search) | Q(email__icontains=search))
    
    limit = min(int(limit), 100) 
    page = max(int(page), 1)
    offset = (page - 1) * limit
    
    total_count = query.count()
    users = query[offset:offset + limit]
    
    users_list = []
    for user in users:
        users_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'avatar_url': user.avatar_url,
            'biography': user.biography
        })
    
    return {
        'success': True,
        'pagination': {
            'page': page,
            'limit': limit,
            'total_count': total_count,
            'total_pages': (total_count + limit - 1) // limit
        },
        'users': users_list
    }

def get_user(user_id: int):
    return CustomUser.objects.filter(id=user_id).first()

def create_user(data: dict):
    create_log("User created", data["username"])
    return CustomUser.objects.create(
        username=data["username"],
        email=data["email"],
        password=make_password(data["password"]),
        role="USER",
        biography=data.get("biography"),
        avatar_url=data.get("avatar_url")
    )

def update_user(user_id: int, data: dict):
    user = CustomUser.objects.filter(id=user_id).first()
    if not user:
        return None

    for field, value in data.items():
        setattr(user, field, value)

    user.save()
    create_log("User updated", user.username)
    return user

def delete_user(user_id: int):
    user = CustomUser.objects.filter(id=user_id).first()
    if not user:
        return False
    user.delete()
    create_log("User deleted", user.username)
    return True