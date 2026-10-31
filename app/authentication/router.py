from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.authentication.schema import UserLogin, UserSignup
from app.authentication.service import login, signup_user

authentication_router = APIRouter()


def signup(
    data: UserSignup,
    db: Session = Depends(get_db),
):
    user = signup_user(data, db)

    return {
        "id": user.id,
        "email": user.email,
        "phone_number": user.phone_number,
        "country_code": user.country_code,
        "role": user.role,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login_at": user.last_login_at,
    }


def login_endpoint(
    request: UserLogin,
    db: Session = Depends(get_db),
):
    return login(request, db)


authentication_router.post("/signup")(signup)
authentication_router.post("/login")(login_endpoint)
