from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class AdminUserCreate(BaseModel):
    """Admin user creation schema"""
    username: str
    email: EmailStr
    password: str
    role: str = "admin"
    is_active: bool = True


class AdminUserUpdate(BaseModel):
    """Admin user update schema"""
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    permissions: Optional[dict] = None


class AdminUserResponse(BaseModel):
    """Admin user response schema (without sensitive data)"""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    permissions: Optional[dict] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str