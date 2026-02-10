from fastapi import APIRouter, Depends, HTTPException
from api import router
from api.schemas.product import ProductCreate, ProductOut
from api.crud.product import (
    list_products,
    get_product,
    create_product,
    update_product,
    delete_product,
    record_product_view,
    record_product_purchase,
    get_product_price_info
)
from shared.security import require_roles

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=list[ProductOut], dependencies=[Depends(require_roles("USER", "EDITOR" ,"ADMIN"))])
def get_products():
    return list_products()

@router.get("/{product_id}", response_model=ProductOut, dependencies=[Depends(require_roles("USER", "EDITOR" ,"ADMIN"))])
def get_one_product(product_id: int):
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("", response_model=ProductOut, dependencies=[Depends(require_roles("EDITOR" ,"ADMIN"))])
def create_new_product(product: ProductCreate):
    return create_product(product.model_dump())

@router.put("/{product_id}", response_model=ProductOut, dependencies=[Depends(require_roles("EDITOR" ,"ADMIN"))])
def update_existing_product(product_id: int, product: ProductCreate):
    updated = update_product(product_id, product.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@router.delete("/{product_id}", dependencies=[Depends(require_roles("ADMIN"))])
def delete_existing_product(product_id: int):
    if not delete_product(product_id):
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


