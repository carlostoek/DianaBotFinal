from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Dict, Any, Optional
from database.connection import get_db
from database.models import (
    User, UserBalance, Subscription, NarrativeFragment, 
    UserNarrativeProgress, Mission, UserMission, Achievement, 
    UserAchievement, ChannelPost, AdminUser, ConversionFunnel
)
from api.middleware.auth import require_role, get_current_active_user
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter(prefix="/analytics", tags=["analytics"])


class MetricsSummaryResponse(BaseModel):
    engagement: Dict[str, Any]
    monetization: Dict[str, Any]
    narrative: Dict[str, Any]
    gamification: Dict[str, Any]
    technical: Dict[str, Any]


class EngagementMetricsResponse(BaseModel):
    dau: int
    wau: int
    mau: int
    avg_session_length_minutes: float
    retention_rate_7d: float
    retention_rate_30d: float


class MonetizationMetricsResponse(BaseModel):
    active_vip_subs: int
    conversion_rate: float
    mrr: float
    arpu: float
    lifetime_value: float


class NarrativeMetricsResponse(BaseModel):
    fragments_completed_today: int
    avg_level_completion: float
    most_popular_decision: str
    avg_time_to_complete_fragment: float
    completion_rate: float


class GamificationMetricsResponse(BaseModel):
    besitos_in_circulation: int
    transactions_today: int
    missions_completed_today: int
    achievements_unlocked_today: int
    active_missions: int


@router.get("/summary", response_model=MetricsSummaryResponse)
async def get_metrics_summary(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get comprehensive metrics summary"""
    now = datetime.now()
    
    # Engagement metrics
    dau = count_active_users(db, hours=24)
    wau = count_active_users(db, days=7)
    mau = count_active_users(db, days=30)
    
    # Monetization metrics
    active_vip_subs = count_active_subscriptions(db)
    conversion_rate = calculate_conversion_rate(db)
    
    # Narrative metrics
    fragments_completed_today = count_completions(db, hours=24)
    avg_level_completion = get_avg_level_completion(db)
    
    # Gamification metrics
    besitos_in_circulation = get_total_besitos(db)
    transactions_today = count_transactions(db, hours=24)
    
    return MetricsSummaryResponse(
        engagement={
            "dau": dau,
            "wau": wau,
            "mau": mau,
            "avg_session_length_minutes": 0.0,  # Placeholder
            "retention_rate_7d": 0.0,  # Placeholder
            "retention_rate_30d": 0.0  # Placeholder
        },
        monetization={
            "active_vip_subs": active_vip_subs,
            "conversion_rate": conversion_rate,
            "mrr": 0.0,  # Placeholder
            "arpu": 0.0,  # Placeholder
            "lifetime_value": 0.0  # Placeholder
        },
        narrative={
            "fragments_completed_today": fragments_completed_today,
            "avg_level_completion": avg_level_completion,
            "most_popular_decision": "",  # Placeholder
            "avg_time_to_complete_fragment": 0.0,  # Placeholder
            "completion_rate": 0.0  # Placeholder
        },
        gamification={
            "besitos_in_circulation": besitos_in_circulation,
            "transactions_today": transactions_today,
            "missions_completed_today": 0,  # Placeholder
            "achievements_unlocked_today": 0,  # Placeholder
            "active_missions": 0  # Placeholder
        },
        technical={
            "avg_response_time_ms": 0.0,  # Placeholder
            "error_rate_percent": 0.0,  # Placeholder
            "uptime_percent": 100.0,  # Placeholder
            "cache_hit_rate_percent": 0.0  # Placeholder
        }
    )


@router.get("/engagement", response_model=EngagementMetricsResponse)
async def get_engagement_metrics(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get engagement metrics"""
    dau = count_active_users(db, hours=24)
    wau = count_active_users(db, days=7)
    mau = count_active_users(db, days=30)
    
    return EngagementMetricsResponse(
        dau=dau,
        wau=wau,
        mau=mau,
        avg_session_length_minutes=0.0,  # Placeholder
        retention_rate_7d=0.0,  # Placeholder
        retention_rate_30d=0.0  # Placeholder
    )


@router.get("/monetization", response_model=MonetizationMetricsResponse)
async def get_monetization_metrics(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get monetization metrics"""
    active_vip_subs = count_active_subscriptions(db)
    conversion_rate = calculate_conversion_rate(db)
    
    return MonetizationMetricsResponse(
        active_vip_subs=active_vip_subs,
        conversion_rate=conversion_rate,
        mrr=0.0,  # Placeholder
        arpu=0.0,  # Placeholder
        lifetime_value=0.0  # Placeholder
    )


@router.get("/narrative", response_model=NarrativeMetricsResponse)
async def get_narrative_metrics(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get narrative metrics"""
    fragments_completed_today = count_completions(db, hours=24)
    avg_level_completion = get_avg_level_completion(db)
    
    return NarrativeMetricsResponse(
        fragments_completed_today=fragments_completed_today,
        avg_level_completion=avg_level_completion,
        most_popular_decision="",  # Placeholder
        avg_time_to_complete_fragment=0.0,  # Placeholder
        completion_rate=0.0  # Placeholder
    )


@router.get("/gamification", response_model=GamificationMetricsResponse)
async def get_gamification_metrics(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get gamification metrics"""
    besitos_in_circulation = get_total_besitos(db)
    transactions_today = count_transactions(db, hours=24)
    
    return GamificationMetricsResponse(
        besitos_in_circulation=besitos_in_circulation,
        transactions_today=transactions_today,
        missions_completed_today=0,  # Placeholder
        achievements_unlocked_today=0,  # Placeholder
        active_missions=0  # Placeholder
    )


# Helper functions for metrics calculation
def count_active_users(db: Session, hours: Optional[int] = 24, days: Optional[int] = None) -> int:
    """Count active users in given time period"""
    if hours:
        cutoff_time = datetime.now() - timedelta(hours=hours)
    elif days:
        cutoff_time = datetime.now() - timedelta(days=days)
    else:
        cutoff_time = datetime.now() - timedelta(days=1)
    
    # TODO: Implement actual active user counting based on last_active field
    # For now, return total user count
    return db.query(User).count()


def count_active_subscriptions(db: Session) -> int:
    """Count active VIP subscriptions"""
    return db.query(Subscription).filter(
        Subscription.status == "active",
        Subscription.tier == "vip"
    ).count()


def calculate_conversion_rate(db: Session) -> float:
    """Calculate conversion rate to VIP"""
    total_users = db.query(User).count()
    vip_users = db.query(Subscription).filter(
        Subscription.status == "active",
        Subscription.tier == "vip"
    ).count()
    
    if total_users == 0:
        return 0.0
    
    return (vip_users / total_users) * 100


def count_completions(db: Session, hours: Optional[int] = 24, days: Optional[int] = None) -> int:
    """Count narrative fragment completions in given time period"""
    if hours:
        cutoff_time = datetime.now() - timedelta(hours=hours)
    elif days:
        cutoff_time = datetime.now() - timedelta(days=days)
    else:
        cutoff_time = datetime.now() - timedelta(days=1)
    
    # TODO: Implement actual completion counting based on completion timestamps
    # For now, return total progress count
    return db.query(UserNarrativeProgress).count()


def get_avg_level_completion(db: Session) -> float:
    """Get average level completion rate"""
    # TODO: Implement actual average level completion calculation
    # For now, return placeholder
    return 0.0


def get_total_besitos(db: Session) -> int:
    """Get total besitos in circulation"""
    result = db.query(func.sum(UserBalance.besitos)).scalar()
    return result if result else 0


def count_transactions(db: Session, hours: Optional[int] = 24, days: Optional[int] = None) -> int:
    """Count transactions in given time period"""
    # TODO: Implement actual transaction counting
    # For now, return placeholder
    return 0


@router.get("/users/growth")
async def get_user_growth(
    period: str = "7d",  # 7d, 30d, 90d
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get user growth metrics over time"""
    if period == "7d":
        days = 7
    elif period == "30d":
        days = 30
    elif period == "90d":
        days = 90
    else:
        days = 7
    
    # TODO: Implement actual user growth calculation
    # For now, return placeholder data
    return {
        "period": period,
        "total_users": db.query(User).count(),
        "new_users_today": 0,
        "growth_rate": 0.0,
        "data": []  # Time series data
    }


@router.get("/revenue/trends")
async def get_revenue_trends(
    period: str = "30d",
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get revenue trends over time"""
    # TODO: Implement actual revenue trend calculation
    # For now, return placeholder data
    return {
        "period": period,
        "total_revenue": 0.0,
        "revenue_today": 0.0,
        "growth_rate": 0.0,
        "data": []  # Time series data
    }


@router.get("/")
async def get_dashboard_analytics(
    period: str = "30d",
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get analytics data for dashboard"""
    # Calculate period dates
    now = datetime.now()
    if period == "7d":
        start_date = now - timedelta(days=7)
    elif period == "30d":
        start_date = now - timedelta(days=30)
    elif period == "90d":
        start_date = now - timedelta(days=90)
    elif period == "1y":
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=30)

    # Get metrics
    active_users = count_active_users(db, days=(now - start_date).days) or 0
    messages_today = count_messages_today(db)
    besitos_earned = get_besitos_earned(db, start_date)
    stories_read = count_stories_read(db, start_date)

    # Get top users (placeholder - need to implement based on actual activity)
    top_users = [
        {"id": 1, "name": "Usuario 1", "score": 150},
        {"id": 2, "name": "Usuario 2", "score": 120},
        {"id": 3, "name": "Usuario 3", "score": 100},
        {"id": 4, "name": "Usuario 4", "score": 90},
        {"id": 5, "name": "Usuario 5", "score": 80}
    ]

    # Get popular content (placeholder)
    popular_content = [
        {"id": 1, "title": "Capítulo 1", "views": 250},
        {"id": 2, "title": "Capítulo 2", "views": 200},
        {"id": 3, "title": "Capítulo 3", "views": 180},
        {"id": 4, "title": "Capítulo 4", "views": 150},
        {"id": 5, "title": "Capítulo 5", "views": 120}
    ]

    # Get top achievements (placeholder)
    top_achievements = [
        {"id": 1, "name": "Primer Mensaje", "count": 45},
        {"id": 2, "name": "Trivia Experto", "count": 32},
        {"id": 3, "name": "Misión Completada", "count": 28},
        {"id": 4, "name": "Historia Completa", "count": 20},
        {"id": 5, "name": "VIP Activo", "count": 15}
    ]

    # Generate chart data (placeholder time series)
    chart_data = generate_chart_data(period)

    return {
        "metrics": {
            "activeUsers": active_users,
            "messagesToday": messages_today,
            "besitosEarned": besitos_earned,
            "storiesRead": stories_read
        },
        "topUsers": top_users,
        "popularContent": popular_content,
        "topAchievements": top_achievements,
        "chartData": chart_data
    }


def count_messages_today(db: Session) -> int:
    """Count messages sent today"""
    # TODO: Implement actual message counting
    # For now, return placeholder
    return 42


def get_besitos_earned(db: Session, start_date: datetime) -> int:
    """Get total besitos earned in period"""
    # TODO: Implement actual besitos earned calculation
    # For now, return placeholder
    return 1250


def count_stories_read(db: Session, start_date: datetime) -> int:
    """Count stories read in period"""
    # TODO: Implement actual story read counting
    # For now, return placeholder
    return 89


def generate_chart_data(period: str) -> list:
    """Generate placeholder chart data"""
    if period == "7d":
        days = 7
        labels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    elif period == "30d":
        days = 30
        labels = [f"Día {i+1}" for i in range(days)]
    elif period == "90d":
        days = 12
        labels = [f"Sem {i+1}" for i in range(days)]
    elif period == "1y":
        days = 12
        labels = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    else:
        days = 30
        labels = [f"Día {i+1}" for i in range(days)]

    # Generate random data for demonstration
    import random
    data = []
    for i in range(len(labels)):
        data.append(random.randint(10, 100))

    return data


@router.get("/conversion-funnels")
async def get_conversion_funnel_analytics(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get conversion funnel analytics"""
    try:
        # Get funnel statistics
        total_funnels = db.query(ConversionFunnel).count()
        active_funnels = db.query(ConversionFunnel).filter(
            ConversionFunnel.is_active == True
        ).count()
        completed_funnels = db.query(ConversionFunnel).filter(
            ConversionFunnel.is_completed == True
        ).count()
        
        # Get funnel types distribution
        funnel_types = db.query(
            ConversionFunnel.funnel_type,
            func.count(ConversionFunnel.id).label('count')
        ).group_by(ConversionFunnel.funnel_type).all()
        
        # Get stage distribution
        stage_distribution = db.query(
            ConversionFunnel.stage_current,
            func.count(ConversionFunnel.id).label('count')
        ).filter(
            ConversionFunnel.is_active == True
        ).group_by(ConversionFunnel.stage_current).all()
        
        # Get conversion rates by funnel type
        conversion_rates = []
        for funnel_type in ['free_to_vip', 'engagement_to_purchase', 'free_to_purchaser']:
            total_type = db.query(ConversionFunnel).filter(
                ConversionFunnel.funnel_type == funnel_type
            ).count()
            
            completed_type = db.query(ConversionFunnel).filter(
                ConversionFunnel.funnel_type == funnel_type,
                ConversionFunnel.is_completed == True
            ).count()
            
            conversion_rate = (completed_type / total_type * 100) if total_type > 0 else 0
            
            conversion_rates.append({
                'funnel_type': funnel_type,
                'total': total_type,
                'completed': completed_type,
                'conversion_rate': round(conversion_rate, 2)
            })
        
        # Get average time to conversion
        avg_time_query = db.query(
            func.avg(
                func.extract('epoch', ConversionFunnel.completed_at - ConversionFunnel.entered_at) / 86400
            ).label('avg_days')
        ).filter(
            ConversionFunnel.is_completed == True
        ).scalar()
        
        avg_time_to_conversion = round(avg_time_query or 0, 2)
        
        # Get recent conversions (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_conversions = db.query(ConversionFunnel).filter(
            ConversionFunnel.is_completed == True,
            ConversionFunnel.completed_at >= thirty_days_ago
        ).count()
        
        return {
            "summary": {
                "total_funnels": total_funnels,
                "active_funnels": active_funnels,
                "completed_funnels": completed_funnels,
                "avg_time_to_conversion_days": avg_time_to_conversion,
                "recent_conversions_30d": recent_conversions
            },
            "funnel_types": [
                {"type": funnel_type, "count": count}
                for funnel_type, count in funnel_types
            ],
            "stage_distribution": [
                {"stage": stage, "count": count}
                for stage, count in stage_distribution
            ],
            "conversion_rates": conversion_rates
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversion funnel analytics: {str(e)}"
        )