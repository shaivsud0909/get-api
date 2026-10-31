from fastapi import APIRouter

from app.authentication.router import login_endpoint, signup


authentication_router = APIRouter()



authentication_router.post("/signup")(signup)
authentication_router.post("/login")(login_endpoint)
