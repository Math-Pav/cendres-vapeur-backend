from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from decimal import Decimal
from django.apps import apps
from django.db.models import Count, Q
from apps.models.product import Product 
from apps.models.vote import Vote 

router = APIRouter()

# --- SCHÉMAS ---

class VotePayload(BaseModel):
    user_id: int
    note: int = Field(..., ge=1, le=10, description="Note entre 1 et 10")
    comment: str | None = Field(None, description="Ton avis écrit")
    like: bool = Field(True, description="Est-ce que tu aimes le produit ? (True/False)")

class LikePayload(BaseModel):
    user_id: int

# Nouveau schéma pour l'affichage du classement
class ProductRankingSchema(BaseModel):
    rank: int
    product_name: str
    price: float
    total_likes: int

# ==========================================
# 1. POST : VOTER (FULL PACKAGE)
# ==========================================
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


# ==========================================
# 2. POST : TOGGLE LIKE
# ==========================================
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


# ==========================================
# 3. GET : CLASSEMENT PAR LIKES (LE TOP) 🏆
# ==========================================
# 👇 CHANGEMENT ICI : "/ranking" au lieu de "/products/ranking"
@router.get("/ranking", response_model=List[ProductRankingSchema])
def get_products_ranking():
    """
    Affiche la liste des produits triés par nombre de LIKES (du + aimé au - aimé).
    """
    # On demande à Django de compter les votes où like=True
    # Puis on trie par ce nombre (descendant)
    products = Product.objects.annotate(
        like_count=Count('votes', filter=Q(votes__like=True))
    ).order_by('-like_count')

    results = []
    for index, p in enumerate(products):
        results.append({
            "rank": index + 1,          # 1er, 2ème, 3ème...
            "product_name": p.name,
            "price": float(p.current_price),
            "total_likes": p.like_count
        })

    return results