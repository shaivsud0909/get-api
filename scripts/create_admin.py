"""Create an admin account using the application's SQLAlchemy model and bcrypt hash.

Run from the project root:
    uv sync
    uv run python scripts/create_admin.py --dry-run
    uv run python scripts/create_admin.py

The email is fixed below. The password and confirmation are prompted for without
echoing them to the terminal. Use --dry-run to validate the database operation
and roll it back without creating an account. Optional phone details are handled
like the user signup fields.
"""

from __future__ import annotations

import argparse
import getpass
import secrets
import sys
from pathlib import Path

# Make project imports work when invoked as `python scripts/create_admin.py`.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import Field, ValidationError
from passlib.exc import MissingBackendError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.authentication.schema import UserSignup

ADMIN_EMAIL = "prakriti@gmail.com"


class AdminSignup(UserSignup):
    """Signup validation for this script, allowing passwords shorter than 8 chars."""

    password: str = Field(min_length=1, max_length=128)


def create_admin(
    db: Session,
    email: str,
    password: str,
    *,
    phone_number: str | None = None,
    country_code: str | None = None,
    dry_run: bool = False,
) -> bool:
    """Create an admin and return False when the normalized email already exists."""
    signup = AdminSignup(
        email=email,
        password=password,
        phone_number=phone_number,
        country_code=country_code,
    )
    normalized_email = str(signup.email).lower()

    try:
        from app.authentication.utils import hash_password
        from app.database.models import User

        existing_user = db.query(User).filter(User.email == normalized_email).first()
        if existing_user is not None:
            db.rollback()
            return False

        admin = User(
            email=normalized_email,
            password_hash=hash_password(signup.password),
            phone_number=signup.phone_number,
            country_code=signup.country_code,
            role="admin",
            is_active=True,
            is_verified=True,
            is_deleted=False,
        )
        db.add(admin)

        if dry_run:
            db.flush()
            db.rollback()
            return True

        db.commit()
        return True
    except Exception:
        db.rollback()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an admin account.")
    parser.add_argument("--phone-number", help="Optional phone number.")
    parser.add_argument("--country-code", help="Optional country calling code.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check the account and database write, then roll back without creating it.",
    )
    args = parser.parse_args()

    email = ADMIN_EMAIL
    password = getpass.getpass("Admin password: ")
    confirmation = getpass.getpass("Confirm password: ")

    if not secrets.compare_digest(password, confirmation):
        print("Passwords do not match.", file=sys.stderr)
        return 2

    try:
        # Validate before opening a database session using the admin script's
        # password length rule and the shared signup email/phone fields.
        signup = AdminSignup(
            email=email,
            password=password,
            phone_number=args.phone_number,
            country_code=args.country_code,
        )
        email = str(signup.email).lower()
    except ValidationError as exc:
        for error in exc.errors(include_input=False):
            location = ".".join(str(part) for part in error["loc"])
            print(f"Invalid {location}: {error['msg']}.", file=sys.stderr)
        return 2

    db: Session | None = None
    try:
        # Importing this reads the application's settings and creates its
        # existing engine/session factory. Keep configuration errors reportable.
        from app.database.connection import SessionLocal

        db = SessionLocal()
        created = create_admin(
            db,
            email,
            password,
            phone_number=args.phone_number,
            country_code=args.country_code,
            dry_run=args.dry_run,
        )
        if not created:
            print(f"A user with email {email} already exists; no changes were made.")
            return 1

        if args.dry_run:
            print(f"Dry run succeeded for {email}; no account was created.")
        else:
            print(f"Admin account created for {email}.")
        return 0
    except ValidationError as exc:
        print(
            "Configuration or account data is invalid; check the project settings and input.",
            file=sys.stderr,
        )
        return 2
    except MissingBackendError:
        if db is not None:
            db.rollback()
        print(
            "Password hashing backend is missing. Run `uv sync` to install the declared bcrypt dependency, then retry.",
            file=sys.stderr,
        )
        return 1
    except SQLAlchemyError:
        if db is not None:
            db.rollback()
        print("Database operation failed; no admin account was created.", file=sys.stderr)
        return 1
    except Exception:
        if db is not None:
            db.rollback()
        print("Admin creation failed; no password details were recorded.", file=sys.stderr)
        return 1
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    raise SystemExit(main())
