from fastapi import APIRouter
from app.agents.product_owner.routes import router as product_owner_router

router = APIRouter()

router.include_router(product_owner_router, prefix="/product-owner")
