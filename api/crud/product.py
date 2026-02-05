from apps.models import Product, Category

def list_products():
    return Product.objects.all()

def get_product(product_id: int):
    return Product.objects.filter(id=product_id).first()

def create_product(data: dict):
    category = Category.objects.get(id=data["category_id"])
    return Product.objects.create(
        name=data["name"],
        description=data.get("description"),
        stock=data["stock"],
        image=data.get("image_url"),
        category=category,
        base_price=data["base_price"],
        current_price=data["current_price"],
        popularity_score=data["popularity_score"]
    )

def update_product(product_id: int, data: dict):
    product = Product.objects.filter(id=product_id).first()
    if not product:
        return None

    for field, value in data.items():
        setattr(product, field, value)

    product.save()
    return product

def delete_product(product_id: int):
    product = Product.objects.filter(id=product_id).first()
    if not product:
        return False
    product.delete()
    return True