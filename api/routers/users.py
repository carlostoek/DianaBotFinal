from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database.connection import get_db
from database.models import User, UserBalance, Subscription, AdminUser
from api.middleware.auth import require_role, get_current_active_user
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    language_code: Optional[str]
    is_premium: Optional[bool]
    created_at: str
    updated_at: str


class UserStatsResponse(BaseModel):
    user_id: int
    telegram_id: int
    username: Optional[str]
    balance: int
    subscription_tier: Optional[str]
    subscription_status: Optional[str]
    total_fragments_completed: int
    total_missions_completed: int
    total_achievements_unlocked: int
    total_besitos_earned: int
    total_besitos_spent: int


class GrantBesitosRequest(BaseModel):
    amount: int
    reason: str


class UpdateSubscriptionRequest(BaseModel):
    tier: str
    status: str


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get paginated list of users"""
    users = db.query(User).offset(skip).limit(limit).all()
    
    return [
        UserResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code,
            is_premium=user.is_premium,
            created_at=user.created_at.isoformat() if user.created_at else "",
            updated_at=user.updated_at.isoformat() if user.updated_at else ""
        )
        for user in users
    ]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
        is_premium=user.is_premium,
        created_at=user.created_at.isoformat() if user.created_at else "",
        updated_at=user.updated_at.isoformat() if user.updated_at else ""
    )


@router.get("/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get detailed stats for a user"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Get user balance
    balance = db.query(UserBalance).filter(UserBalance.user_id == user_id).first()
    
    # Get subscription info
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    
    # TODO: Implement actual stats calculation
    # For now, return placeholder values
    return UserStatsResponse(
        user_id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        balance=balance.besitos if balance else 0,
        subscription_tier=subscription.subscription_type if subscription else None,
        subscription_status=subscription.status if subscription else None,
        total_fragments_completed=0,  # Placeholder
        total_missions_completed=0,   # Placeholder
        total_achievements_unlocked=0, # Placeholder
        total_besitos_earned=0,       # Placeholder
        total_besitos_spent=0         # Placeholder
    )


@router.put("/{user_id}/subscription")
async def update_user_subscription(
    user_id: int,
    subscription_data: UpdateSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Update user subscription"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Get or create subscription
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    
    if not subscription:
        subscription = Subscription(
            user_id=user_id,
            subscription_type=subscription_data.tier,
            status=subscription_data.status
        )
        db.add(subscription)
    else:
        subscription.subscription_type = subscription_data.tier
        subscription.status = subscription_data.status
    
    db.commit()
    
    return {
        "message": f"Subscription updated for user {user_id}",
        "tier": subscription.subscription_type,
        "status": subscription.status
    }


@router.post("/{user_id}/grant-besitos")
async def grant_besitos(
    user_id: int,
    request: GrantBesitosRequest,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Grant besitos to a user"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Get or create balance
    balance = db.query(UserBalance).filter(UserBalance.user_id == user_id).first()
    
    if not balance:
        balance = UserBalance(user_id=user_id, besitos=request.amount)
        db.add(balance)
    else:
        balance.besitos += request.amount
    
    # TODO: Create transaction record
    
    db.commit()
    
    return {
        "message": f"Granted {request.amount} besitos to user {user_id}",
        "new_balance": balance.besitos,
        "reason": request.reason
    }