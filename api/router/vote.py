
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List
from decimal import Decimal
from django.apps import apps
from shared.security import require_roles


try:
    from apps.models.product import Product
    from apps.models.vote import Vote
except ImportError:

    Product = None
    Vote = None

router = APIRouter()


class VotePayload(BaseModel):
    user_id: int
    note: int = Field(..., ge=1, le=10, description="Note entre 1 et 10")
    comment: str | None = Field(None, description="Ton avis écrit")
    like: bool = Field(True, description="Est-ce que tu aimes le produit ? (True/False)")

class LikePayload(BaseModel):
    user_id: int

class ProductRankingSchema(BaseModel):
    rank: int
    product_name: str
    price: float
    total_likes: int



@router.post("/products/{product_id}/vote", dependencies=[Depends(require_roles("USER", "EDITOR", "ADMIN"))])
def vote_product(product_id: int, payload: VotePayload):
    if Product is None or Vote is None:
        raise HTTPException(status_code=500, detail="Erreur interne : Modèles non trouvés.")

    try:
       
        try:
            User = apps.get_model('apps', 'CustomUser')
        except LookupError:
            from django.contrib.auth import get_user_model
            User = get_user_model()

        if not User.objects.filter(id=payload.user_id).exists():
            raise HTTPException(status_code=404, detail="Utilisateur inconnu.")
        
        if not Product.objects.filter(id=product_id).exists():
            raise HTTPException(status_code=404, detail="Produit inconnu.")

        
        vote, created = Vote.objects.update_or_create(
            user_id=payload.user_id,
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
            "message": "Avis enregistré !",
            "note": vote.note,
            "liked": vote.like,
            "new_price": product.current_price
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products/{product_id}/like", dependencies=[Depends(require_roles("USER", "EDITOR", "ADMIN"))])
def toggle_like(product_id: int, payload: LikePayload):
    if Vote is None:
        raise HTTPException(status_code=500, detail="Erreur interne : Modèle Vote non trouvé.")
        
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


@router.get("/ranking", response_model=List[ProductRankingSchema], dependencies=[Depends(require_roles("USER", "EDITOR", "ADMIN"))])
def get_products_ranking():
    if Product is None or Vote is None:
        raise HTTPException(status_code=500, detail="Impossible de charger les données.")

    try:

        
        all_products = Product.objects.all()
        ranking_list = []

        for p in all_products:
            
            likes = Vote.objects.filter(product_id=p.id, like=True).count()
            
            ranking_list.append({
                "product_name": p.name,
                "price": float(p.current_price),
                "total_likes": likes
            })

        
        ranking_list.sort(key=lambda x: x['total_likes'], reverse=True)

        
        final_results = []
        for index, item in enumerate(ranking_list):
            final_results.append({
                "rank": index + 1,
                "product_name": item['product_name'],
                "price": item['price'],
                "total_likes": item['total_likes']
            })

        return final_results

    except Exception as e:
       
        print(f"ERREUR RANKING: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de classement: {str(e)}")









