from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode the JWT bearer token and return the authenticated User.
    Raises 401 if token is missing/invalid, 403 if account is inactive.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is malformed.",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token no longer exists.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Please contact an administrator.",
        )

    return user


def require_roles(*roles: UserRole):
    """
    Role-guard factory. Returns a FastAPI dependency that:
    - Authenticates the user via JWT
    - Checks their role against the allowed roles list
    - Returns the authenticated User object on success
    - Raises HTTP 403 if the role is not permitted

    Usage:
        @router.get("/admin-only")
        def endpoint(user: User = Depends(require_roles(UserRole.admin))):
            ...

        @router.delete("/record", dependencies=[Depends(require_roles(UserRole.admin))])
        def delete():
            ...
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            allowed = [r.value for r in roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Your role '{current_user.role.value}' is not "
                       f"permitted. Required: {allowed}",
            )
        return current_user

    return role_checker
