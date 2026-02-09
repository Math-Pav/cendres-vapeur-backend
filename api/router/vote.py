from fastapi import APIRouter, HTTPException, status
from decimal import Decimal
from django.apps import apps
from apps.models.product import Product 
from apps.models.vote import Vote 

router = APIRouter()

@router.post("/products/{product_id}/vote")
def vote_algorithm(product_id: int, user_id: int):
    """
    Permet à un utilisateur existant de voter pour un produit existant.
    Applique l'inflation de 1% sur le prix.
    """
    try:
        # 1. Vérification : L'utilisateur existe-t-il ?
        # On récupère le bon modèle d'utilisateur dynamiquement
        try:
            User = apps.get_model('apps', 'CustomUser')
        except LookupError:
            from django.contrib.auth import get_user_model
            User = get_user_model()

        if not User.objects.filter(id=user_id).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"L'utilisateur avec l'ID {user_id} n'existe pas."
            )

        # 2. Vérification : Le produit existe-t-il ?
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Le produit avec l'ID {product_id} n'existe pas."
            )

        # 3. Vérification : A-t-il déjà voté ?
        if Vote.objects.filter(user_id=user_id, product_id=product_id).exists():
            return {
                "status": "info",
                "message": "Cet utilisateur a déjà voté pour ce produit.",
                "current_price": product.current_price
            }

        # 4. Action : Enregistrement du vote
        Vote.objects.create(user_id=user_id, product_id=product_id)

        # 5. Action : Algorithme Économique (Inflation +1%)
        product.previous_price = product.current_price
        product.popularity_score += 1.0
        product.current_price = product.current_price * Decimal('1.01')
        
        # Calcul du pourcentage de variation pour l'affichage
        if product.previous_price > 0:
            delta = product.current_price - product.previous_price
            product.price_change_percentage = float((delta / product.previous_price) * 100)
            
        product.save()

        return {
            "status": "success", 
            "message": "Vote accepté.", 
            "new_price": product.current_price,
            "variation": f"+{product.price_change_percentage:.2f}%"
        }

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        # Gestion des erreurs imprévues
        raise HTTPException(status_code=500, detail=str(e))