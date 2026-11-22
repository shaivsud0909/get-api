from fastapi import Depends, HTTPException, Request
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


async def user_required(request: Request, token: str = Depends(oauth)):
    try:
        payload = decode_access_token(token)

        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        if payload.get("role") != "user":
            raise HTTPException(status_code=403, detail="User access only")

        request.state.user = payload
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def any_role_required(request: Request, token: str = Depends(oauth)):
    """Allow any authenticated user or admin; exposes the payload on request.state.user."""
    try:
        payload = decode_access_token(token)

        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        if payload.get("role") not in ("user", "admin"):
            raise HTTPException(status_code=403, detail="Access denied")

        request.state.user = payload
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
