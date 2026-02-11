from fastapi import APIRouter, Depends, HTTPException
from api import router
from api.schemas.product import ProductCreate, ProductOut
from api.crud.product import (
    list_products,
    list_products_advanced,
    get_product,
    create_product,
    update_product,
    delete_product,
    record_product_view,
    record_product_purchase,
    get_product_price_info,
    get_product_votes,
    get_product_likes_count,
    get_top_products_by_sales
)
from shared.security import require_roles

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=list[ProductOut], dependencies=[Depends(require_roles("USER", "EDITOR" ,"ADMIN"))])
def get_products():
    return list_products()

@router.get("/search", response_model=dict, dependencies=[Depends(require_roles("USER", "EDITOR" ,"ADMIN"))])
def search_products(search: str = None, category_id: int = None, min_price: float = None, 
                   max_price: float = None, sort: str = 'id', order: str = 'asc',
                   page: int = 1, limit: int = 20):
    """
    Recherche et filtre les produits avec pagination et tri
    
    Query params:
    - search: Recherche par nom ou description
    - category_id: Filtrer par catégorie (ID)
    - min_price: Prix minimum
    - max_price: Prix maximum
    - sort: Champ de tri (id, name, price, popularity, stock, purchase_count)
    - order: Ordre (asc, desc)
    - page: Numéro de page (default: 1)
    - limit: Résultats par page (default: 20, max: 100)
    
    Roles allowed: USER, EDITOR, ADMIN
    """
    result = list_products_advanced(
        search=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        order=order,
        page=page,
        limit=limit
    )
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error', 'Error fetching products'))
    return result

@router.get("/{product_id}", response_model=ProductOut, dependencies=[Depends(require_roles("USER", "EDITOR" ,"ADMIN"))])
def get_one_product(product_id: int):
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("", response_model=ProductOut)
def create_new_product(product: ProductCreate, payload = Depends(require_roles("EDITOR" ,"ADMIN"))):
    return create_product(product.model_dump(), user_id=payload['id'])

@router.put("/{product_id}", response_model=ProductOut)
def update_existing_product(product_id: int, product: ProductCreate, payload = Depends(require_roles("EDITOR" ,"ADMIN"))):
    updated = update_product(product_id, product.model_dump(), user_id=payload['id'])
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@router.delete("/{product_id}")
def delete_existing_product(product_id: int, payload = Depends(require_roles("ADMIN"))):
    if not delete_product(product_id, user_id=payload['id']):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"deleted": True}

@router.get("/{product_id}/price-info", dependencies=[Depends(require_roles("USER", "EDITOR" ,"ADMIN"))])
def get_price_info(product_id: int):
    """
    Récupère les infos complètes du prix d'un produit
    Inclut: prix actuel, variation %, offre/demande, indicateur
    """
    result = get_product_price_info(product_id)
    if not result.get('success'):
        raise HTTPException(status_code=404, detail=result.get('error', 'Product not found'))
    return result

@router.post("/{product_id}/view", dependencies=[Depends(require_roles("USER", "EDITOR" ,"ADMIN"))])
def register_product_view(product_id: int):
    """
    Enregistre une consultation d'un produit
    Augmente la demande et recalcule le prix
    Appeler cet endpoint chaque fois qu'un client consulte un produit
    """
    result = record_product_view(product_id)
    if not result.get('success'):
        raise HTTPException(status_code=404, detail=result.get('error', 'Product not found'))
    return result

@router.post("/{product_id}/purchase", dependencies=[Depends(require_roles("USER", "EDITOR" ,"ADMIN"))])
def register_product_purchase(product_id: int, quantity: int = 1):
    """
    Enregistre un achat d'un produit
    Réduit le stock et recalcule le prix (achat pèse 3x plus dans la demande)
    
    Query params:
    - quantity: nombre d'unités à acheter (default: 1)
    """
    if quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")
    
    result = record_product_purchase(product_id, quantity)
    if not result.get('success'):
        error_msg = result.get('error', 'Product not found')
        status_code = 400 if 'stock' in error_msg.lower() else 404
        raise HTTPException(status_code=status_code, detail=error_msg)
    
    return result

@router.get("/{product_id}/votes", dependencies=[Depends(require_roles("USER", "EDITOR" ,"ADMIN"))])
def get_product_reviews(product_id: int):
    """
    Récupère tous les votes, notes et commentaires d'un produit
    Affiche les détails de chaque vote avec infos utilisateur
    
    Retourne:
    - Tous les votes avec notes, commentaires et likes
    - Contexte statistique (nombre total, moyenne des notes)
    """
    result = get_product_votes(product_id)
    if not result.get('success'):
        raise HTTPException(status_code=404, detail=result.get('error', 'Product not found'))
    return result

@router.get("/{product_id}/likes-count", dependencies=[Depends(require_roles("USER", "EDITOR" ,"ADMIN"))])
def get_likes_summary(product_id: int):
    """
    Récupère le nombre de likes et statistiques rapides d'un produit
    
    Retourne:
    - Nombre total de likes
    - Nombre total de votes
    - Pourcentage de likes
    - Liste des utilisateurs qui ont voté
    """
    result = get_product_likes_count(product_id)
    if not result.get('success'):
        raise HTTPException(status_code=404, detail=result.get('error', 'Product not found'))
    return result

@router.get("/top/sales", dependencies=[Depends(require_roles("ADMIN", "EDITOR"))])
def get_top_selling_products(limit: int = 5):
    """
    Récupère les N produits les plus vendus avec statistiques complètes
    
    Query params:
    - limit: nombre de produits à retourner (default: 5, max: 20)
    
    Retourne:
    - Liste avec: nom, stock, prix, nombre achats, revenu généré
    - Résumé: revenu total, achats totaux, revenu moyen
    
    Roles allowed: ADMIN, EDITOR
    """
    if limit < 1 or limit > 20:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 20")
    
    result = get_top_products_by_sales(limit)
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error', 'Error fetching top products'))
    return result