from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.authentication.utils import hash_password, create_access_token, verify_password
from app.authentication.schema import UserLogin, UserSignup


async def signup_user(data: UserSignup, db: AsyncSession):
    result = await db.execute(
        select(User).where(User.email == str(data.email).lower())
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    user = User(
        email=str(data.email).lower(),
        password_hash=hash_password(data.password),
        phone_number=data.phone_number,
        country_code=data.country_code,
    )
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    except Exception:
        await db.rollback()
        raise

    return user


async def login(request: UserLogin, db: AsyncSession):
    result = await db.execute(
        select(User).where(User.email == str(request.email).lower())
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    user.last_login_at = datetime.now(timezone.utc)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
    })

    return {
        "access_token": token,
        "token_type": "bearer",
    }
