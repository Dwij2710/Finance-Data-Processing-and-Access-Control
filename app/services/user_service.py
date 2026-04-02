from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.core.security import hash_password


def create_user(db: Session, data: UserCreate) -> User:
    """Create a new user. Raises 409 if email is already registered."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A user with email '{data.email}' is already registered.",
        )

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: int) -> User:
    """Fetch a user by ID. Raises 404 if not found."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
    return user


def get_all_users(db: Session) -> List[User]:
    """Return all users in the system."""
    return db.query(User).order_by(User.id).all()


def update_user_role(db: Session, user_id: int, role: UserRole) -> User:
    """Assign a new role to a user."""
    user = get_user_by_id(db, user_id)
    user.role = role
    db.commit()
    db.refresh(user)
    return user


def update_user_status(db: Session, user_id: int, is_active: bool) -> User:
    """Activate or deactivate a user account."""
    user = get_user_by_id(db, user_id)
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int, current_user_id: int) -> None:
    """Delete a user. Prevents self-deletion."""
    if user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account.",
        )
    user = get_user_by_id(db, user_id)
    db.delete(user)
    db.commit()
