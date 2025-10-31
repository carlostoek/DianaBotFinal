from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import AdminUser
from api.middleware.auth import (
    authenticate_user, create_access_token, get_password_hash,
    get_current_active_user, require_role
)
from api.schemas.auth import (
    Token, AdminUserCreate, AdminUserResponse, LoginRequest
)


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint to get JWT token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": access_token_expires.total_seconds()
    }


@router.post("/register", response_model=AdminUserResponse)
async def register_admin_user(
    user_data: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("owner"))
):
    """Register a new admin user (owner only)"""
    # Check if username already exists
    existing_user = db.query(AdminUser).filter(
        (AdminUser.username == user_data.username) | 
        (AdminUser.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new admin user
    hashed_password = get_password_hash(user_data.password)
    db_user = AdminUser(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=user_data.is_active
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return AdminUserResponse.model_validate(db_user)


@router.get("/me", response_model=AdminUserResponse)
async def read_users_me(current_user: AdminUser = Depends(get_current_active_user)):
    """Get current user information"""
    return AdminUserResponse.model_validate(current_user)


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: AdminUser = Depends(get_current_active_user)):
    """Refresh JWT token"""
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": current_user.username, "user_id": current_user.id, "role": current_user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": access_token_expires.total_seconds()
    }