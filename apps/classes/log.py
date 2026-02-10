from apps.models.log import Log
from apps.models.customUser import CustomUser

def create_log(message: str, user=None) -> Log:
    """Crée une entrée de log
    
    Args:
        message: Message du log
        user: Objet utilisateur ou ID utilisateur
    """
    user_obj = None
    
    if user is not None:
        if isinstance(user, int):
            try:
                user_obj = CustomUser.objects.get(id=user)
            except CustomUser.DoesNotExist:
                user_obj = None
        else:
            user_obj = user
    
    log = Log(message=message, user=user_obj)
    log.save()
    return log


def get_logs(user=None, limit: int = 50):
    """Récupère les logs"""
    if user:
        return Log.objects.filter(user=user).order_by('-created_at')[:limit]
    return Log.objects.all().order_by('-created_at')[:limit]


def log_action(request, action: str):
    """Log une action CRUD si utilisateur connecté"""
    if request.user.is_authenticated:
        create_log(action, request.user)
