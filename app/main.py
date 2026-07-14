from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random
from app.core.config import settings
from app.core.db import connect_to_mongo, close_mongo_connection, get_database

from app.routes import auth, products, categories, brands, orders, admin, reviews, location, returns, cod, coupons, banners, notifications, cms, reviews_admin
from app.routes import settings as settings_router

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(brands.router, prefix="/api/brands", tags=["brands"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])
app.include_router(location.router, prefix="/api/location", tags=["location"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(returns.router, prefix="/api/returns", tags=["returns"])
app.include_router(cod.router, prefix="/api/cod", tags=["cod"])
app.include_router(coupons.router, prefix="/api/coupons", tags=["coupons"])
app.include_router(banners.router, prefix="/api/banners", tags=["banners"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(cms.router, prefix="/api/cms", tags=["cms"])
app.include_router(reviews_admin.router, prefix="/api/admin/reviews", tags=["admin_reviews"])

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/")
def read_root():
    return {"message": "Welcome to the OneBasket API"}
