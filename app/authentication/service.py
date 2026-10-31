from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.database.models import User
from app.authentication.utils import hash_password, create_access_token, verify_password
from app.authentication.schema import UserLogin, UserSignup
from sqlalchemy.orm import Session




def signup_user(data: UserSignup, db: Session):

    existing_user = (
        db.query(User)
        .filter(User.email == str(data.email).lower())
        .first()
    )

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
        # role, status flags and timestamps use model/database defaults
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise

    return user







def login(request: UserLogin, db: Session):
    
    #  Find the user by email
    user = (
        db.query(User)
        .filter(User.email == str(request.email).lower())
        .first()
    )

    #  Check credentials
    if not user or not verify_password(
        request.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # 3. Check account status
    if not user.is_active or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    # 4. Update last successful login time
    user.last_login_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    # 5. Generate JWT
    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
    })

    return {
        "access_token": token,
        "token_type": "bearer",
    }

