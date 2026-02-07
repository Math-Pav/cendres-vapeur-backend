from fastapi import APIRouter, HTTPException
from decimal import Decimal
from django.apps import apps 
from apps.models.product import Product 
from apps.models.vote import Vote 

router = APIRouter()

@router.get("/fix-database")
def fix_database_issues():
    report = []
    try:
        
        try:
            RealUser = apps.get_model('apps', 'CustomUser')
            model_name = "CustomUser (apps)"
        except LookupError:
            from django.contrib.auth import get_user_model
            RealUser = get_user_model()
            model_name = "User Standard"

        report.append(f"Cible identifiée : {model_name}")

        
        if not RealUser.objects.filter(id=99).exists():
            u = RealUser.objects.create(
                id=99, 
                username="Sauveur_99", 
                email="sauveur99@api.com",
                password="password123" 
            )
            u.save()
            report.append("Utilisateur ID 99 créé dans la bonne table.")
        else:
            report.append("Utilisateur ID 99 existe déjà.")

        
        if not Product.objects.filter(id=1).exists():
            Product.objects.create(id=1, name="Masque Gaz", current_price=100.0, stock=10)
            report.append("Produit ID 1 créé.")
        else:
            report.append("Produit ID 1 existe déjà.")

        return {"status": "fixed", "user_id_to_use": 99, "details": report}

    except Exception as e:
        return {"status": "error", "details": str(e)}


@router.post("/products/{product_id}/vote")
def vote_algorithm(product_id: int, user_id: int):
    try:

        Vote.objects.create(user_id=user_id, product_id=product_id)

        
        product = Product.objects.get(id=product_id)
        product.previous_price = product.current_price
        product.popularity_score += 1.0
        product.current_price = product.current_price * Decimal('1.01')
        
        if product.previous_price > 0:
            delta = product.current_price - product.previous_price
            product.price_change_percentage = float((delta / product.previous_price) * 100)
            
        product.save()

        return {
            "status": "success", 
            "message": "Vote accepté.", 
            "new_price": product.current_price
        }

    except Exception as e:
        
        if "1452" in str(e):
            raise HTTPException(status_code=400, detail="Erreur : L'utilisateur n'existe pas dans la table cible. Lancez /fix-database.")
        if "1062" in str(e):
             return {"status": "info", "message": "Vote déjà enregistré."}
        
       
        raise HTTPException(status_code=500, detail=str(e))