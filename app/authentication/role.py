from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.authentication.utils import decode_access_token


oauth = OAuth2PasswordBearer(tokenUrl="/login", scheme_name="BearerAuth")


async def admin_required(token: str = Depends(oauth)):
    try:
        payload = decode_access_token(token)

        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin only access")

        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def user_required(token: str = Depends(oauth)):
    try:
        payload = decode_access_token(token)

        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        if payload.get("role") != "user":
            raise HTTPException(status_code=403, detail="User access only")

        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
