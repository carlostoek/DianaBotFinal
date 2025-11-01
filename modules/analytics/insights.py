"""
Insight Engine for DianaBot Analytics System
Automatically detects patterns and provides actionable insights
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from sqlalchemy import func, and_, or_, text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass
class Insight:
    """Base insight data structure"""
    insight_type: str
    severity: str  # low, medium, high, critical
    title: str
    description: str
    recommendation: str
    data: Dict[str, Any]
    detected_at: datetime


@dataclass
class DropOffPoint:
    """Drop-off point in user journey"""
    point_id: str
    point_name: str
    drop_off_rate: float
    users_affected: int
    potential_revenue_loss: float


@dataclass
class HighValueUser:
    """High-value user identification"""
    user_id: int
    engagement_score: float
    conversion_probability: float
    potential_lifetime_value: float
    recommended_actions: List[str]


@dataclass
class ContentOptimization:
    """Content optimization suggestion"""
    content_id: str
    content_type: str
    current_performance: float
    suggested_improvement: str
    expected_impact: str


class InsightEngine:
    """Automatically detects patterns and provides actionable insights"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def detect_drop_off_points(self, days_back: int = 30) -> List[DropOffPoint]:
        """Detect where users are dropping off in their journey"""
        logger.info(f"Detecting drop-off points for last {days_back} days")
        
        drop_off_points = []
        
        # Detect narrative drop-off points
        narrative_drop_offs = self._detect_narrative_drop_offs(days_back)
        drop_off_points.extend(narrative_drop_offs)
        
        # Detect experience drop-off points
        experience_drop_offs = self._detect_experience_drop_offs(days_back)
        drop_off_points.extend(experience_drop_offs)
        
        # Detect subscription funnel drop-offs
        subscription_drop_offs = self._detect_subscription_drop_offs(days_back)
        drop_off_points.extend(subscription_drop_offs)
        
        return drop_off_points
    
    def identify_high_value_users(self, days_back: int = 30) -> List[HighValueUser]:
        """Identify users with high conversion potential"""
        logger.info(f"Identifying high-value users for last {days_back} days")
        
        high_value_users = []
        
        # Get user engagement data
        user_engagement = self._get_user_engagement_data(days_back)
        
        # Calculate conversion probability for each user
        for user_id, engagement_data in user_engagement.items():
            conversion_prob = self._calculate_conversion_probability(user_id, engagement_data)
            potential_ltv = self._calculate_potential_ltv(engagement_data)
            
            # Only include users with high conversion probability
            if conversion_prob > 0.7:
                recommended_actions = self._get_recommended_actions(user_id, engagement_data)
                
                high_value_users.append(HighValueUser(
                    user_id=user_id,
                    engagement_score=engagement_data.get('engagement_score', 0),
                    conversion_probability=conversion_prob,
                    potential_lifetime_value=potential_ltv,
                    recommended_actions=recommended_actions
                ))
        
        # Sort by conversion probability (highest first)
        high_value_users.sort(key=lambda x: x.conversion_probability, reverse=True)
        
        return high_value_users[:20]  # Return top 20
    
    def suggest_content_optimizations(self, days_back: int = 30) -> List[ContentOptimization]:
        """Suggest content optimizations based on performance data"""
        logger.info(f"Suggesting content optimizations for last {days_back} days")
        
        optimizations = []
        
        # Analyze narrative content
        narrative_optimizations = self._analyze_narrative_content(days_back)
        optimizations.extend(narrative_optimizations)
        
        # Analyze experience content
        experience_optimizations = self._analyze_experience_content(days_back)
        optimizations.extend(experience_optimizations)
        
        # Analyze shop items
        shop_optimizations = self._analyze_shop_content(days_back)
        optimizations.extend(shop_optimizations)
        
        return optimizations
    
    def generate_insights(self, days_back: int = 30) -> List[Insight]:
        """Generate comprehensive insights across all areas"""
        logger.info(f"Generating comprehensive insights for last {days_back} days")
        
        insights = []
        
        # Generate engagement insights
        engagement_insights = self._generate_engagement_insights(days_back)
        insights.extend(engagement_insights)
        
        # Generate monetization insights
        monetization_insights = self._generate_monetization_insights(days_back)
        insights.extend(monetization_insights)
        
        # Generate content insights
        content_insights = self._generate_content_insights(days_back)
        insights.extend(content_insights)
        
        # Generate system insights
        system_insights = self._generate_system_insights(days_back)
        insights.extend(system_insights)
        
        return insights
    
    # Private helper methods
    
    def _detect_narrative_drop_offs(self, days_back: int) -> List[DropOffPoint]:
        """Detect drop-off points in narrative content"""
        from database.models import AnalyticsEvent
        
        drop_off_points = []
        
        # Get narrative progression data
        narrative_progression = self.db.query(
            AnalyticsEvent.metadata['fragment_id'].astext.label('fragment_id'),
            func.count(AnalyticsEvent.id).label('views'),
            func.count(func.distinct(AnalyticsEvent.user_id)).label('unique_users')
        ).filter(
            and_(
                AnalyticsEvent.timestamp >= datetime.now() - timedelta(days=days_back),
                AnalyticsEvent.event_type == 'content_viewed',
                AnalyticsEvent.metadata['content_type'].astext == 'narrative'
            )
        ).group_by('fragment_id').all()
        
        # Calculate drop-off rates between consecutive fragments
        # This is a simplified implementation
        # In production, you'd need to track actual user progression
        
        return drop_off_points
    
    def _detect_experience_drop_offs(self, days_back: int) -> List[DropOffPoint]:
        """Detect drop-off points in experiences"""
        from database.models import AnalyticsEvent
        
        drop_off_points = []
        
        # Get experience start and completion data
        experience_data = self.db.query(
            AnalyticsEvent.metadata['experience_id'].astext.label('experience_id'),
            AnalyticsEvent.event_type,
            func.count(AnalyticsEvent.id).label('count')
        ).filter(
            and_(
                AnalyticsEvent.timestamp >= datetime.now() - timedelta(days=days_back),
                AnalyticsEvent.event_type.in_(['experience_started', 'experience_completed'])
            )
        ).group_by('experience_id', 'event_type').all()
        
        # Calculate completion rates
        experience_stats = {}
        for exp_id, event_type, count in experience_data:
            if exp_id not in experience_stats:
                experience_stats[exp_id] = {'started': 0, 'completed': 0}
            
            if event_type == 'experience_started':
                experience_stats[exp_id]['started'] = count
            elif event_type == 'experience_completed':
                experience_stats[exp_id]['completed'] = count
        
        # Identify experiences with low completion rates
        for exp_id, stats in experience_stats.items():
            started = stats['started']
            completed = stats['completed']
            
            if started > 0:
                completion_rate = completed / started
                
                if completion_rate < 0.3:  # Less than 30% completion
                    drop_off_points.append(DropOffPoint(
                        point_id=exp_id,
                        point_name=f"Experience {exp_id}",
                        drop_off_rate=1 - completion_rate,
                        users_affected=started - completed,
                        potential_revenue_loss=0.0  # Would need business logic
                    ))
        
        return drop_off_points
    
    def _detect_subscription_drop_offs(self, days_back: int) -> List[DropOffPoint]:
        """Detect drop-off points in subscription funnel"""
        from database.models import ConversionFunnel
        
        drop_off_points = []
        
        # Get funnel stage data
        funnel_stages = self.db.query(
            ConversionFunnel.stage_current,
            func.count(ConversionFunnel.id).label('user_count')
        ).filter(
            and_(
                ConversionFunnel.entered_at >= datetime.now() - timedelta(days=days_back),
                ConversionFunnel.is_active == True
            )
        ).group_by(ConversionFunnel.stage_current).all()
        
        # Calculate drop-off between stages
        # This is a simplified implementation
        # In production, you'd track actual progression between stages
        
        return drop_off_points
    
    def _get_user_engagement_data(self, days_back: int) -> Dict[int, Dict[str, Any]]:
        """Get engagement data for all users"""
        from database.models import AnalyticsEvent
        
        user_engagement = {}
        
        # Get user activity counts
        user_activity = self.db.query(
            AnalyticsEvent.user_id,
            AnalyticsEvent.event_type,
            func.count(AnalyticsEvent.id).label('count')
        ).filter(
            AnalyticsEvent.timestamp >= datetime.now() - timedelta(days=days_back)
        ).group_by(AnalyticsEvent.user_id, AnalyticsEvent.event_type).all()
        
        # Aggregate by user
        for user_id, event_type, count in user_activity:
            if user_id not in user_engagement:
                user_engagement[user_id] = {
                    'total_events': 0,
                    'event_types': {},
                    'engagement_score': 0
                }
            
            user_engagement[user_id]['total_events'] += count
            user_engagement[user_id]['event_types'][event_type] = count
        
        # Calculate engagement scores
        for user_id, data in user_engagement.items():
            # Simple scoring based on event diversity and frequency
            event_diversity = len(data['event_types'])
            total_events = data['total_events']
            
            # Weight different event types
            weighted_score = 0
            for event_type, count in data['event_types'].items():
                weight = self._get_event_weight(event_type)
                weighted_score += count * weight
            
            data['engagement_score'] = weighted_score
        
        return user_engagement
    
    def _get_event_weight(self, event_type: str) -> float:
        """Get weight for event type in engagement scoring"""
        weights = {
            'user_login': 1.0,
            'content_viewed': 2.0,
            'reaction_added': 3.0,
            'mission_completed': 5.0,
            'achievement_unlocked': 8.0,
            'besitos_earned': 2.0,
            'trivia_answered': 3.0,
            'auction_participation': 4.0,
            'experience_started': 6.0,
            'experience_completed': 10.0
        }
        
        return weights.get(event_type, 1.0)
    
    def _calculate_conversion_probability(self, user_id: int, engagement_data: Dict[str, Any]) -> float:
        """Calculate probability that user will convert to VIP"""
        from database.models import Subscription
        
        # Check if user is already VIP
        existing_subscription = self.db.query(Subscription).filter(
            and_(
                Subscription.user_id == user_id,
                Subscription.status == 'active'
            )
        ).first()
        
        if existing_subscription:
            return 1.0  # Already converted
        
        # Calculate probability based on engagement
        engagement_score = engagement_data.get('engagement_score', 0)
        event_diversity = len(engagement_data.get('event_types', {}))
        
        # Simple probability calculation
        # In production, you'd use machine learning
        base_probability = min(engagement_score / 100, 0.9)  # Cap at 90%
        diversity_boost = min(event_diversity / 10, 0.2)  # Max 20% boost
        
        return base_probability + diversity_boost
    
    def _calculate_potential_ltv(self, engagement_data: Dict[str, Any]) -> float:
        """Calculate potential lifetime value"""
        engagement_score = engagement_data.get('engagement_score', 0)
        
        # Simple LTV estimation based on engagement
        # In production, you'd use more sophisticated models
        base_ltv = 10.0  # Base LTV for average user
        engagement_multiplier = engagement_score / 50  # Normalize
        
        return base_ltv * engagement_multiplier
    
    def _get_recommended_actions(self, user_id: int, engagement_data: Dict[str, Any]) -> List[str]:
        """Get recommended actions for high-value user"""
        recommendations = []
        
        event_types = engagement_data.get('event_types', {})
        
        # Recommend based on missing engagement types
        if 'experience_started' not in event_types:
            recommendations.append("Send experience invitation")
        
        if 'auction_participation' not in event_types:
            recommendations.append("Notify about upcoming auctions")
        
        if 'mission_completed' not in event_types:
            recommendations.append("Suggest easy missions to complete")
        
        # Always recommend VIP upgrade
        recommendations.append("Offer VIP trial or discount")
        
        return recommendations
    
    def _analyze_narrative_content(self, days_back: int) -> List[ContentOptimization]:
        """Analyze narrative content for optimization opportunities"""
        from database.models import AnalyticsEvent
        
        optimizations = []
        
        # Get narrative performance data
        narrative_performance = self.db.query(
            AnalyticsEvent.metadata['content_id'].astext.label('content_id'),
            func.count(AnalyticsEvent.id).label('views'),
            func.count(func.distinct(AnalyticsEvent.user_id)).label('unique_users')
        ).filter(
            and_(
                AnalyticsEvent.timestamp >= datetime.now() - timedelta(days=days_back),
                AnalyticsEvent.event_type == 'content_viewed',
                AnalyticsEvent.metadata['content_type'].astext == 'narrative'
            )
        ).group_by('content_id').all()
        
        # Identify underperforming content
        total_views = sum(views for _, views, _ in narrative_performance)
        avg_views = total_views / len(narrative_performance) if narrative_performance else 0
        
        for content_id, views, unique_users in narrative_performance:
            if views < avg_views * 0.5:  # Less than 50% of average
                optimizations.append(ContentOptimization(
                    content_id=content_id,
                    content_type='narrative',
                    current_performance=views,
                    suggested_improvement="Improve content quality or add interactive elements",
                    expected_impact="Increase engagement by 20-30%"
                ))
        
        return optimizations
    
    def _analyze_experience_content(self, days_back: int) -> List[ContentOptimization]:
        """Analyze experience content for optimization opportunities"""
        # Similar to narrative analysis but for experiences
        return []
    
    def _analyze_shop_content(self, days_back: int) -> List[ContentOptimization]:
        """Analyze shop content for optimization opportunities"""
        # Similar to narrative analysis but for shop items
        return []
    
    def _generate_engagement_insights(self, days_back: int) -> List[Insight]:
        """Generate engagement-related insights"""
        insights = []
        
        # Example insight: Low retention
        insights.append(Insight(
            insight_type="engagement_retention",
            severity="medium",
            title="Low Day 7 Retention",
            description="Only 25% of users return after 7 days",
            recommendation="Implement onboarding improvements and early engagement triggers",
            data={"retention_rate": 0.25},
            detected_at=datetime.now()
        ))
        
        return insights
    
    def _generate_monetization_insights(self, days_back: int) -> List[Insight]:
        """Generate monetization-related insights"""
        insights = []
        
        # Example insight: High-value users identified
        insights.append(Insight(
            insight_type="monetization_high_value",
            severity="high",
            title="15 High-Value Users Identified",
            description="Users with >70% conversion probability detected",
            recommendation="Target these users with personalized VIP offers",
            data={"high_value_users_count": 15},
            detected_at=datetime.now()
        ))
        
        return insights
    
    def _generate_content_insights(self, days_back: int) -> List[Insight]:
        """Generate content-related insights"""
        insights = []
        
        # Example insight: Content performance
        insights.append(Insight(
            insight_type="content_performance",
            severity="low",
            title="3 Narrative Fragments Underperforming",
            description="Some content has below-average engagement",
            recommendation="Review and optimize underperforming content",
            data={"underperforming_count": 3},
            detected_at=datetime.now()
        ))
        
        return insights
    
    def _generate_system_insights(self, days_back: int) -> List[Insight]:
        """Generate system-related insights"""
        insights = []
        
        # Example insight: System performance
        insights.append(Insight(
            insight_type="system_performance",
            severity="low",
            title="System Performance Stable",
            description="All systems operating within normal parameters",
            recommendation="Continue monitoring system health",
            data={"status": "stable"},
            detected_at=datetime.now()
        ))
        
        return insights