from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Alice Admin"])
    email: EmailStr = Field(..., examples=["alice@example.com"])
    password: str = Field(..., min_length=6, examples=["secret123"])
    role: Optional[UserRole] = Field(UserRole.viewer, description="Defaults to 'viewer' if not provided")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., examples=["admin@finance.com"])
    password: str = Field(..., examples=["admin123"])


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RoleUpdate(BaseModel):
    role: UserRole = Field(..., description="New role to assign")


class StatusUpdate(BaseModel):
    is_active: bool = Field(..., description="Set to true to activate, false to deactivate")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
