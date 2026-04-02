from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.user import UserResponse, RoleUpdate, StatusUpdate
from app.services import user_service
from app.models.user import User, UserRole
from app.core.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get your own user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return current_user


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="[Admin] List all users",
)
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    """**Admin only.** Return all users registered in the system."""
    return user_service.get_all_users(db)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="[Admin] Get a specific user by ID",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    """**Admin only.** Fetch details of a specific user by their ID."""
    return user_service.get_user_by_id(db, user_id)


@router.put(
    "/{user_id}/role",
    response_model=UserResponse,
    summary="[Admin] Update a user's role",
)
def update_role(
    user_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    """**Admin only.** Assign a new role (viewer / analyst / admin) to a user."""
    return user_service.update_user_role(db, user_id, data.role)


@router.put(
    "/{user_id}/status",
    response_model=UserResponse,
    summary="[Admin] Activate or deactivate a user",
)
def update_status(
    user_id: int,
    data: StatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    """**Admin only.** Toggle a user's active/inactive status."""
    return user_service.update_user_status(db, user_id, data.is_active)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Delete a user",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    """
    **Admin only.** Permanently delete a user account.

    - You cannot delete your own account.
    """
    user_service.delete_user(db, user_id, current_user.id)
