from fastapi import APIRouter, Depends, HTTPException
from apps.classes.log import get_logs
from shared.security import require_roles

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.get("", dependencies=[Depends(require_roles("ADMIN"))])
def get_all_logs(limit: int = 50):
    """
    Récupère tous les logs du système
    
    Query params:
    - limit: Nombre maximum de logs à retourner (default: 50)
    
    Roles allowed: ADMIN
    """
    try:
        logs = get_logs(limit=limit)
        
        logs_list = []
        for log in logs:
            logs_list.append({
                'id': log.id,
                'message': log.message,
                'created_at': log.created_at.isoformat(),
                'user': {
                    'id': log.user.id,
                    'username': log.user.username,
                    'email': log.user.email
                } if log.user else None
            })
        
        return {
            'success': True,
            'total': len(logs_list),
            'logs': logs_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", dependencies=[Depends(require_roles("ADMIN"))])
def get_user_logs(user_id: int, limit: int = 50):
    """
    Récupère tous les logs d'un utilisateur spécifique
    
    Path params:
    - user_id: ID de l'utilisateur
    
    Query params:
    - limit: Nombre maximum de logs à retourner (default: 50)
    
    Roles allowed: ADMIN
    """
    try:
        from apps.models.customUser import CustomUser
        
        user = CustomUser.objects.filter(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        logs = get_logs(user=user, limit=limit)
        
        logs_list = []
        for log in logs:
            logs_list.append({
                'id': log.id,
                'message': log.message,
                'created_at': log.created_at.isoformat(),
                'user': {
                    'id': log.user.id,
                    'username': log.user.username,
                    'email': log.user.email
                } if log.user else None
            })
        
        return {
            'success': True,
            'user_id': user_id,
            'username': user.username,
            'total': len(logs_list),
            'logs': logs_list
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
