from apps.models.log import Log


def create_log(message: str, user) -> Log:
    """Crée une entrée de log"""
    log = Log(message=message, user=user)
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
