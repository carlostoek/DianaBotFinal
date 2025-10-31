from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database.connection import get_db
from database.models import (
    NarrativeFragment, Mission, Achievement, Item, 
    Channel, ChannelPost, AdminUser
)
from api.middleware.auth import require_role, get_current_active_user
from pydantic import BaseModel

router = APIRouter(prefix="/content", tags=["content"])


# Narrative Models
class NarrativeFragmentCreate(BaseModel):
    fragment_key: str
    title: str
    content: str
    decisions: Optional[dict] = None
    requirements: Optional[dict] = None
    rewards: Optional[dict] = None
    is_active: bool = True


class NarrativeFragmentResponse(BaseModel):
    id: int
    fragment_key: str
    title: str
    content: str
    decisions: Optional[dict]
    requirements: Optional[dict]
    rewards: Optional[dict]
    is_active: bool
    created_at: str
    updated_at: str


# Gamification Models
class MissionCreate(BaseModel):
    mission_key: str
    title: str
    description: str
    requirements: dict
    rewards: dict
    is_active: bool = True


class MissionResponse(BaseModel):
    id: int
    mission_key: str
    title: str
    description: str
    requirements: dict
    rewards: dict
    is_active: bool
    created_at: str
    updated_at: str


class AchievementCreate(BaseModel):
    achievement_key: str
    title: str
    description: str
    requirements: dict
    rewards: dict
    is_active: bool = True


class AchievementResponse(BaseModel):
    id: int
    achievement_key: str
    title: str
    description: str
    requirements: dict
    rewards: dict
    is_active: bool
    created_at: str
    updated_at: str


class ItemCreate(BaseModel):
    item_key: str
    name: str
    description: str
    item_type: str
    rarity: str
    effects: Optional[dict] = None
    is_active: bool = True


class ItemResponse(BaseModel):
    id: int
    item_key: str
    name: str
    description: str
    item_type: str
    rarity: str
    effects: Optional[dict]
    is_active: bool
    created_at: str
    updated_at: str


# Channel Models
class ChannelCreate(BaseModel):
    channel_id: int
    channel_name: str
    channel_username: Optional[str] = None
    is_active: bool = True


class ChannelResponse(BaseModel):
    id: int
    channel_id: int
    channel_name: str
    channel_username: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str


class ChannelPostCreate(BaseModel):
    channel_id: int
    content: str
    scheduled_time: Optional[str] = None
    status: str = "draft"


class ChannelPostResponse(BaseModel):
    id: int
    channel_id: int
    content: str
    scheduled_time: Optional[str]
    status: str
    published_at: Optional[str]
    created_at: str
    updated_at: str


# Narrative Endpoints
@router.get("/narrative/fragments", response_model=List[NarrativeFragmentResponse])
async def get_narrative_fragments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get paginated list of narrative fragments"""
    fragments = db.query(NarrativeFragment).offset(skip).limit(limit).all()
    
    return [
        NarrativeFragmentResponse(
            id=fragment.id,
            fragment_key=fragment.fragment_key,
            title=fragment.title,
            content=fragment.content,
            decisions=fragment.decisions,
            requirements=fragment.requirements,
            rewards=fragment.rewards,
            is_active=fragment.is_active,
            created_at=fragment.created_at.isoformat() if fragment.created_at else None,
            updated_at=fragment.updated_at.isoformat() if fragment.updated_at else None
        )
        for fragment in fragments
    ]


@router.post("/narrative/fragments", response_model=NarrativeFragmentResponse)
async def create_narrative_fragment(
    fragment_data: NarrativeFragmentCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Create a new narrative fragment"""
    # Check if fragment key already exists
    existing = db.query(NarrativeFragment).filter(
        NarrativeFragment.fragment_key == fragment_data.fragment_key
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fragment with key '{fragment_data.fragment_key}' already exists"
        )
    
    fragment = NarrativeFragment(
        fragment_key=fragment_data.fragment_key,
        title=fragment_data.title,
        content=fragment_data.content,
        decisions=fragment_data.decisions,
        requirements=fragment_data.requirements,
        rewards=fragment_data.rewards,
        is_active=fragment_data.is_active
    )
    
    db.add(fragment)
    db.commit()
    db.refresh(fragment)
    
    return NarrativeFragmentResponse(
        id=fragment.id,
        fragment_key=fragment.fragment_key,
        title=fragment.title,
        content=fragment.content,
        decisions=fragment.decisions,
        requirements=fragment.requirements,
        rewards=fragment.rewards,
        is_active=fragment.is_active,
        created_at=fragment.created_at.isoformat() if fragment.created_at else None,
        updated_at=fragment.updated_at.isoformat() if fragment.updated_at else None
    )


@router.put("/narrative/fragments/{fragment_id}", response_model=NarrativeFragmentResponse)
async def update_narrative_fragment(
    fragment_id: int,
    fragment_data: NarrativeFragmentCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Update a narrative fragment"""
    fragment = db.query(NarrativeFragment).filter(NarrativeFragment.id == fragment_id).first()
    
    if not fragment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fragment with ID {fragment_id} not found"
        )
    
    # Update fields
    fragment.fragment_key = fragment_data.fragment_key
    fragment.title = fragment_data.title
    fragment.content = fragment_data.content
    fragment.decisions = fragment_data.decisions
    fragment.requirements = fragment_data.requirements
    fragment.rewards = fragment_data.rewards
    fragment.is_active = fragment_data.is_active
    
    db.commit()
    db.refresh(fragment)
    
    return NarrativeFragmentResponse(
        id=fragment.id,
        fragment_key=fragment.fragment_key,
        title=fragment.title,
        content=fragment.content,
        decisions=fragment.decisions,
        requirements=fragment.requirements,
        rewards=fragment.rewards,
        is_active=fragment.is_active,
        created_at=fragment.created_at.isoformat() if fragment.created_at else None,
        updated_at=fragment.updated_at.isoformat() if fragment.updated_at else None
    )


@router.delete("/narrative/fragments/{fragment_id}")
async def delete_narrative_fragment(
    fragment_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Delete a narrative fragment"""
    fragment = db.query(NarrativeFragment).filter(NarrativeFragment.id == fragment_id).first()
    
    if not fragment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fragment with ID {fragment_id} not found"
        )
    
    db.delete(fragment)
    db.commit()
    
    return {"message": f"Fragment {fragment_id} deleted successfully"}


# Gamification Endpoints
@router.get("/missions", response_model=List[MissionResponse])
async def get_missions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get paginated list of missions"""
    missions = db.query(Mission).offset(skip).limit(limit).all()
    
    return [
        MissionResponse(
            id=mission.id,
            mission_key=mission.mission_key,
            title=mission.title,
            description=mission.description,
            requirements=mission.requirements,
            rewards=mission.rewards,
            is_active=mission.is_active,
            created_at=mission.created_at.isoformat() if mission.created_at else None,
            updated_at=mission.updated_at.isoformat() if mission.updated_at else None
        )
        for mission in missions
    ]


@router.get("/achievements", response_model=List[AchievementResponse])
async def get_achievements(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get paginated list of achievements"""
    achievements = db.query(Achievement).offset(skip).limit(limit).all()
    
    return [
        AchievementResponse(
            id=achievement.id,
            achievement_key=achievement.achievement_key,
            title=achievement.title,
            description=achievement.description,
            requirements=achievement.requirements,
            rewards=achievement.rewards,
            is_active=achievement.is_active,
            created_at=achievement.created_at.isoformat() if achievement.created_at else None,
            updated_at=achievement.updated_at.isoformat() if achievement.updated_at else None
        )
        for achievement in achievements
    ]


@router.get("/items", response_model=List[ItemResponse])
async def get_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get paginated list of items"""
    items = db.query(Item).offset(skip).limit(limit).all()
    
    return [
        ItemResponse(
            id=item.id,
            item_key=item.item_key,
            name=item.name,
            description=item.description,
            item_type=item.item_type,
            rarity=item.rarity,
            effects=item.effects,
            is_active=item.is_active,
            created_at=item.created_at.isoformat() if item.created_at else None,
            updated_at=item.updated_at.isoformat() if item.updated_at else None
        )
        for item in items
    ]


# Channel Endpoints
@router.get("/channels", response_model=List[ChannelResponse])
async def get_channels(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get paginated list of channels"""
    channels = db.query(Channel).offset(skip).limit(limit).all()
    
    return [
        ChannelResponse(
            id=channel.id,
            channel_id=channel.channel_id,
            channel_name=channel.channel_name,
            channel_username=channel.channel_username,
            is_active=channel.is_active,
            created_at=channel.created_at.isoformat() if channel.created_at else None,
            updated_at=channel.updated_at.isoformat() if channel.updated_at else None
        )
        for channel in channels
    ]


@router.get("/channels/{channel_id}/posts", response_model=List[ChannelPostResponse])
async def get_channel_posts(
    channel_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get paginated list of posts for a channel"""
    posts = db.query(ChannelPost).filter(
        ChannelPost.channel_id == channel_id
    ).offset(skip).limit(limit).all()
    
    return [
        ChannelPostResponse(
            id=post.id,
            channel_id=post.channel_id,
            content=post.content,
            scheduled_time=post.scheduled_time.isoformat() if post.scheduled_time else None,
            status=post.status,
            published_at=post.published_at.isoformat() if post.published_at else None,
            created_at=post.created_at.isoformat() if post.created_at else None,
            updated_at=post.updated_at.isoformat() if post.updated_at else None
        )
        for post in posts
    ]