from fastapi import APIRouter



user_router = APIRouter()


user_router.get("/products")()