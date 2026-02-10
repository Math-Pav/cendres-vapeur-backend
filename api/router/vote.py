from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from decimal import Decimal
from django.apps import apps
from apps.models.product import Product 
from apps.models.vote import Vote 

router = APIRouter()

class VotePayload(BaseModel):
    user_id: int
    note: int = Field(..., ge=1, le=10, description="Note entre 1 et 10")
    comment: str | None = Field(None, description="Ton avis écrit")
    like: bool = Field(True, description="Est-ce que tu aimes le produit ? (True/False)")

class LikePayload(BaseModel):
    user_id: int

@router.post("/products/{product_id}/vote")
def vote_product(product_id: int, payload: VotePayload):
    try:
        user_id = payload.user_id
        
        try:
            User = apps.get_model('apps', 'CustomUser')
        except LookupError:
            from django.contrib.auth import get_user_model
            User = get_user_model()

        if not User.objects.filter(id=user_id).exists():
            raise HTTPException(status_code=404, detail="Utilisateur inconnu.")
        
        if not Product.objects.filter(id=product_id).exists():
            raise HTTPException(status_code=404, detail="Produit inconnu.")

        vote, created = Vote.objects.update_or_create(
            user_id=user_id,
            product_id=product_id,
            defaults={
                'note': payload.note,
                'comment': payload.comment,
                'like': payload.like  
            }
        )

        product = Product.objects.get(id=product_id)
        if created:
            product.previous_price = product.current_price
            product.popularity_score += 1.0
            product.current_price = product.current_price * Decimal('1.01')
            product.save()

        return {
            "status": "success", 
            "message": "Review complète enregistrée !",
            "note": vote.note,
            "comment": vote.comment,
            "liked": vote.like,
            "new_price": product.current_price
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products/{product_id}/like")
def toggle_like(product_id: int, payload: LikePayload):
    """
    Active ou Désactive le Like sans toucher au commentaire.
    """
    try:
        vote, created = Vote.objects.get_or_create(
            user_id=payload.user_id, 
            product_id=product_id,
            defaults={'note': 0, 'comment': None, 'like': False}
        )

        vote.like = not vote.like
        vote.save()

        status_message = "LIKED" if vote.like else "UNLIKED"
        total_likes = Vote.objects.filter(product_id=product_id, like=True).count()

        return {
            "status": "success",
            "action": status_message,
            "is_liked": vote.like,
            "total_likes": total_likes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))