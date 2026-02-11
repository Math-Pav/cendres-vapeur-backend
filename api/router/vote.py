from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from decimal import Decimal
from django.apps import apps

# ⚠️ IMPORTANT : On importe les modèles, on ne les recrée pas ici !
# Si ça plante ici, c'est que tes fichiers models/product.py ou models/vote.py n'existent pas.
try:
    from apps.models.product import Product
    from apps.models.vote import Vote
except ImportError:
    # Si l'import échoue, on évite le crash immédiat du serveur, 
    # mais les routes renverront une erreur 500.
    Product = None
    Vote = None

router = APIRouter()

# --- SCHÉMAS ---
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

# ==========================================
# 1. POST : VOTER
# ==========================================
@router.post("/products/{product_id}/vote")
def vote_product(product_id: int, payload: VotePayload):
    if Product is None or Vote is None:
        raise HTTPException(status_code=500, detail="Erreur interne : Modèles non trouvés.")

    try:
        # On charge l'utilisateur dynamiquement pour éviter les conflits
        try:
            User = apps.get_model('apps', 'CustomUser')
        except LookupError:
            from django.contrib.auth import get_user_model
            User = get_user_model()

        if not User.objects.filter(id=payload.user_id).exists():
            raise HTTPException(status_code=404, detail="Utilisateur inconnu.")
        
        if not Product.objects.filter(id=product_id).exists():
            raise HTTPException(status_code=404, detail="Produit inconnu.")

        # Création ou mise à jour du vote
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
            # Logique d'inflation
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

# ==========================================
# 2. POST : TOGGLE LIKE
# ==========================================
@router.post("/products/{product_id}/like")
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
        # Compte manuel simple pour éviter les erreurs de "related_name"
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
# 3. GET : CLASSEMENT (Méthode Robuste)
# ==========================================
@router.get("/ranking", response_model=List[ProductRankingSchema])
def get_products_ranking():
    if Product is None or Vote is None:
        raise HTTPException(status_code=500, detail="Impossible de charger les données.")

    try:
        # MÉTHODE SECURISEE : 
        # Au lieu de demander à la base de données de faire des calculs complexes (annotate),
        # On le fait nous-mêmes en Python. C'est plus sûr si les modèles sont fragiles.
        
        all_products = Product.objects.all()
        ranking_list = []

        for p in all_products:
            # On compte les likes directement dans la table Vote
            likes = Vote.objects.filter(product_id=p.id, like=True).count()
            
            ranking_list.append({
                "product_name": p.name,
                "price": float(p.current_price),
                "total_likes": likes
            })

        # On trie la liste en Python (du plus grand nombre de likes au plus petit)
        # key=lambda x: x['total_likes'] -> on trie sur les likes
        # reverse=True -> Descendant (Grand vers Petit)
        ranking_list.sort(key=lambda x: x['total_likes'], reverse=True)

        # On ajoute le rang (1er, 2ème...) après le tri
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
        # Si ça plante encore, on saura exactement pourquoi
        print(f"ERREUR RANKING: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de classement: {str(e)}")