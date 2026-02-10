import os
import django
from fastapi import FastAPI


# 1. Init Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# 2. Imports des Routeurs (Tes fichiers rangés)
from api.router.auth import router as auth_router
from api.router.order import router as order_router
from api.router.user import router as user_router
from api.router.category import router as category_router
from api.router.colonyEvent import router as colony_event_router
from api.router.orderItem import router as order_item_router
from api.router.product import router as product_router
from api.router.shiftNote import router as shift_note_router
# --- AJOUT DU VOTE ICI ---
from api.router.vote import router as vote_router

# 3. Création de l'application
app = FastAPI(title="Orders API")



# 4. Activation des routes
app.include_router(auth_router)
app.include_router(order_router)
app.include_router(user_router)
app.include_router(category_router)
app.include_router(colony_event_router)
app.include_router(order_item_router)
app.include_router(product_router)
app.include_router(shift_note_router)
# --- ACTIVATION DU VOTE ---
app.include_router(vote_router)