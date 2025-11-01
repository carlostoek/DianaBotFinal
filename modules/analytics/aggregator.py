"""
Metrics Aggregator for DianaBot Analytics System
Aggregates and computes metrics from raw analytics events
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from sqlalchemy import func, and_, or_, text
from sqlalchemy.orm import Session
from database.models import AnalyticsEvent, Transaction, User, Subscription

logger = logging.getLogger(__name__)


@dataclass
class TimeRange:
    """Time range for metrics aggregation"""
    start_date: datetime
    end_date: datetime
    
    @classmethod
    def last_7_days(cls):
        """Get time range for last 7 days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        return cls(start_date, end_date)
    
    @classmethod
    def last_30_days(cls):
        """Get time range for last 30 days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return cls(start_date, end_date)
    
    @classmethod
    def this_month(cls):
        """Get time range for current month"""
        now = datetime.now()
        start_date = datetime(now.year, now.month, 1)
        end_date = now
        return cls(start_date, end_date)


@dataclass
class EngagementMetrics:
    """Engagement metrics data structure"""
    mau: int  # Monthly Active Users
    dau: int  # Daily Active Users
    retention_d1: float  # Day 1 retention
    retention_d7: float  # Day 7 retention
    retention_d30: float  # Day 30 retention
    avg_session_duration: float  # Average session duration in seconds
    engagement_by_module: Dict[str, int]  # Engagement count by module


@dataclass
class MonetizationMetrics:
    """Monetization metrics data structure"""
    total_revenue: float
    arpu: float  # Average Revenue Per User
    arppu: float  # Average Revenue Per Paying User
    free_to_vip_conversion: float  # Conversion rate from free to VIP
    ltv: float  # Lifetime Value
    revenue_by_product: Dict[str, float]  # Revenue breakdown by product


@dataclass
class NarrativeMetrics:
    """Narrative metrics data structure"""
    most_visited_fragments: List[Dict[str, Any]]
    completion_rate: float  # Narrative completion rate
    popular_decisions: List[Dict[str, Any]]
    drop_off_points: List[Dict[str, Any]]


@dataclass
class ExperienceMetrics:
    """Experience metrics data structure"""
    start_rate: float  # Experience start rate
    completion_rate: float  # Experience completion rate
    avg_completion_time: float  # Average completion time in seconds
    popular_experiences: List[Dict[str, Any]]


class MetricsAggregator:
    """Aggregates and computes metrics from analytics data"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_engagement_metrics(self, time_range: TimeRange) -> EngagementMetrics:
        """Get engagement metrics for the given time range"""
        logger.info(f"Computing engagement metrics for {time_range}")
        
        # Get MAU (Monthly Active Users)
        mau = self._get_monthly_active_users(time_range)
        
        # Get DAU (Daily Active Users)
        dau = self._get_daily_active_users(time_range)
        
        # Get retention rates
        retention_d1 = self._get_retention_rate(time_range, days=1)
        retention_d7 = self._get_retention_rate(time_range, days=7)
        retention_d30 = self._get_retention_rate(time_range, days=30)
        
        # Get average session duration
        avg_session_duration = self._get_avg_session_duration(time_range)
        
        # Get engagement by module
        engagement_by_module = self._get_engagement_by_module(time_range)
        
        return EngagementMetrics(
            mau=mau,
            dau=dau,
            retention_d1=retention_d1,
            retention_d7=retention_d7,
            retention_d30=retention_d30,
            avg_session_duration=avg_session_duration,
            engagement_by_module=engagement_by_module
        )
    
    def get_monetization_metrics(self, time_range: TimeRange) -> MonetizationMetrics:
        """Get monetization metrics for the given time range"""
        logger.info(f"Computing monetization metrics for {time_range}")
        
        # Get total revenue
        total_revenue = self._get_total_revenue(time_range)
        
        # Get ARPU (Average Revenue Per User)
        arpu = self._get_arpu(time_range)
        
        # Get ARPPU (Average Revenue Per Paying User)
        arppu = self._get_arppu(time_range)
        
        # Get free to VIP conversion rate
        free_to_vip_conversion = self._get_free_to_vip_conversion(time_range)
        
        # Get LTV (Lifetime Value)
        ltv = self._get_ltv(time_range, avg_customer_lifetime_months=6)
        
        # Get revenue by product
        revenue_by_product = self._get_revenue_by_product(time_range)
        
        return MonetizationMetrics(
            total_revenue=total_revenue,
            arpu=arpu,
            arppu=arppu,
            free_to_vip_conversion=free_to_vip_conversion,
            ltv=ltv,
            revenue_by_product=revenue_by_product
        )
    
    def get_narrative_metrics(self, time_range: TimeRange) -> NarrativeMetrics:
        """Get narrative metrics for the given time range"""
        logger.info(f"Computing narrative metrics for {time_range}")
        
        # Get most visited fragments
        most_visited_fragments = self._get_most_visited_fragments(time_range)
        
        # Get completion rate
        completion_rate = self._get_narrative_completion_rate(time_range)
        
        # Get popular decisions
        popular_decisions = self._get_popular_decisions(time_range)
        
        # Get drop-off points
        drop_off_points = self._get_drop_off_points(time_range)
        
        return NarrativeMetrics(
            most_visited_fragments=most_visited_fragments,
            completion_rate=completion_rate,
            popular_decisions=popular_decisions,
            drop_off_points=drop_off_points
        )
    
    def get_experience_metrics(self, time_range: TimeRange) -> ExperienceMetrics:
        """Get experience metrics for the given time range"""
        logger.info(f"Computing experience metrics for {time_range}")
        
        # Get start rate
        start_rate = self._get_experience_start_rate(time_range)
        
        # Get completion rate
        completion_rate = self._get_experience_completion_rate(time_range)
        
        # Get average completion time
        avg_completion_time = self._get_avg_experience_completion_time(time_range)
        
        # Get popular experiences
        popular_experiences = self._get_popular_experiences(time_range)
        
        return ExperienceMetrics(
            start_rate=start_rate,
            completion_rate=completion_rate,
            avg_completion_time=avg_completion_time,
            popular_experiences=popular_experiences
        )
    
    # Private helper methods for metric calculations
    
    def _get_monthly_active_users(self, time_range: TimeRange) -> int:
        """Get monthly active users count"""
        result = self.db.query(func.count(func.distinct(AnalyticsEvent.user_id))).filter(
            and_(
                AnalyticsEvent.timestamp >= time_range.start_date,
                AnalyticsEvent.timestamp <= time_range.end_date
            )
        ).scalar()
        
        return result or 0
    
    def _get_daily_active_users(self, time_range: TimeRange) -> int:
        """Get daily active users count (average over time range)"""
        # Get unique users per day and average
        daily_counts = self.db.query(
            func.date(AnalyticsEvent.timestamp),
            func.count(func.distinct(AnalyticsEvent.user_id))
        ).filter(
            and_(
                AnalyticsEvent.timestamp >= time_range.start_date,
                AnalyticsEvent.timestamp <= time_range.end_date
            )
        ).group_by(func.date(AnalyticsEvent.timestamp)).all()
        
        if not daily_counts:
            return 0
        
        total_dau = sum(count for _, count in daily_counts)
        avg_dau = total_dau / len(daily_counts)
        
        return int(avg_dau)
    
    def _get_retention_rate(self, time_range: TimeRange, days: int) -> float:
        """Get retention rate for given number of days"""
        
        # Ensure we have enough data for the retention period
        if days <= 0:
            return 0.0
            
        # Get users who had activity in the first day of the range
        cohort_start = time_range.start_date
        cohort_end = cohort_start + timedelta(days=1)
        
        cohort_users = self.db.query(func.distinct(AnalyticsEvent.user_id)).filter(
            and_(
                AnalyticsEvent.timestamp >= cohort_start,
                AnalyticsEvent.timestamp <= cohort_end
            )
        ).all()
        
        if not cohort_users:
            return 0.0
        
        cohort_user_ids = [user_id for (user_id,) in cohort_users]
        
        # Check how many of these users were active after N days
        # Use a window of 3 days around the target day to account for variability
        retention_start = cohort_start + timedelta(days=max(1, days - 1))
        retention_end = cohort_start + timedelta(days=days + 1)
        
        # Ensure we don't exceed the time range end date
        if retention_end > time_range.end_date:
            return 0.0
        
        retained_users = self.db.query(func.distinct(AnalyticsEvent.user_id)).filter(
            and_(
                AnalyticsEvent.timestamp >= retention_start,
                AnalyticsEvent.timestamp <= retention_end,
                AnalyticsEvent.user_id.in_(cohort_user_ids)
            )
        ).count()
        
        retention_rate = retained_users / len(cohort_user_ids) if cohort_user_ids else 0.0
        return round(retention_rate * 100, 2)  # Return as percentage
    
    def _get_avg_session_duration(self, time_range: TimeRange) -> float:
        """Get average session duration in seconds"""
        # This would require session tracking in the events
        # For now, return a placeholder value
        return 300.0  # 5 minutes average
    
    def _get_engagement_by_module(self, time_range: TimeRange) -> Dict[str, int]:
        """Get engagement count by module"""
        
        # Group events by event_type (which corresponds to modules)
        module_engagement = self.db.query(
            AnalyticsEvent.event_type,
            func.count(AnalyticsEvent.id)
        ).filter(
            and_(
                AnalyticsEvent.timestamp >= time_range.start_date,
                AnalyticsEvent.timestamp <= time_range.end_date
            )
        ).group_by(AnalyticsEvent.event_type).all()
        
        return {module: count for module, count in module_engagement}
    
    def _get_total_revenue(self, time_range: TimeRange) -> float:
        """Get total revenue for time range"""
        
        result = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.created_at >= time_range.start_date,
                Transaction.created_at <= time_range.end_date,
                Transaction.status == 'completed'
            )
        ).scalar()
        
        return float(result or 0)
    
    def _get_arpu(self, time_range: TimeRange) -> float:
        """Get Average Revenue Per User"""
        total_revenue = self._get_total_revenue(time_range)
        total_users = self._get_monthly_active_users(time_range)
        
        return total_revenue / total_users if total_users > 0 else 0.0
    
    def _get_arppu(self, time_range: TimeRange) -> float:
        """Get Average Revenue Per Paying User"""
        
        total_revenue = self._get_total_revenue(time_range)
        
        # Count unique paying users
        paying_users = self.db.query(func.count(func.distinct(Transaction.user_id))).filter(
            and_(
                Transaction.created_at >= time_range.start_date,
                Transaction.created_at <= time_range.end_date,
                Transaction.status == 'completed'
            )
        ).scalar()
        
        return total_revenue / paying_users if paying_users > 0 else 0.0
    
    def _get_free_to_vip_conversion(self, time_range: TimeRange) -> float:
        """Get free to VIP conversion rate within time range"""
        
        # Get users who were free at the start of the time range
        free_users_at_start = self.db.query(func.count(User.id)).filter(
            ~User.id.in_(
                self.db.query(Subscription.user_id).filter(
                    Subscription.created_at < time_range.start_date,
                    Subscription.status == 'active'
                )
            )
        ).scalar()
        
        if free_users_at_start == 0:
            return 0.0
        
        # Get users who converted to VIP during the time range
        converted_users = self.db.query(func.count(func.distinct(Subscription.user_id))).filter(
            and_(
                Subscription.created_at >= time_range.start_date,
                Subscription.created_at <= time_range.end_date,
                Subscription.status == 'active'
            )
        ).scalar()
        
        conversion_rate = converted_users / free_users_at_start
        return round(conversion_rate * 100, 2)  # Return as percentage
    
    def _get_ltv(self, time_range: TimeRange, avg_customer_lifetime_months: int = 6) -> float:
        """Get Lifetime Value (simplified calculation)"""
        # Simplified LTV calculation
        arpu = self._get_arpu(time_range)
        
        return arpu * avg_customer_lifetime_months
    
    def _get_revenue_by_product(self, time_range: TimeRange) -> Dict[str, float]:
        """Get revenue breakdown by product"""
        
        revenue_by_product = self.db.query(
            Transaction.product_type,
            func.sum(Transaction.amount)
        ).filter(
            and_(
                Transaction.created_at >= time_range.start_date,
                Transaction.created_at <= time_range.end_date,
                Transaction.status == 'completed'
            )
        ).group_by(Transaction.product_type).all()
        
        return {product_type: float(amount) for product_type, amount in revenue_by_product}
    
    def _get_most_visited_fragments(self, time_range: TimeRange) -> List[Dict[str, Any]]:
        """Get most visited narrative fragments"""
        
        fragments = self.db.query(
            AnalyticsEvent.metadata['content_id'].astext.label('fragment_id'),
            func.count(AnalyticsEvent.id).label('visit_count')
        ).filter(
            and_(
                AnalyticsEvent.timestamp >= time_range.start_date,
                AnalyticsEvent.timestamp <= time_range.end_date,
                AnalyticsEvent.event_type == 'content_viewed',
                AnalyticsEvent.metadata['content_type'].astext == 'narrative'
            )
        ).group_by('fragment_id').order_by(func.count(AnalyticsEvent.id).desc()).limit(10).all()
        
        return [
            {'fragment_id': fragment_id, 'visit_count': visit_count}
            for fragment_id, visit_count in fragments
        ]
    
    def _get_narrative_completion_rate(self, time_range: TimeRange) -> float:
        """Get narrative completion rate"""
        # This would require tracking narrative progress
        # For now, return a placeholder value
        return 0.65  # 65% completion rate
    
    def _get_popular_decisions(self, time_range: TimeRange) -> List[Dict[str, Any]]:
        """Get popular narrative decisions"""
        
        decisions = self.db.query(
            AnalyticsEvent.metadata['decision_id'].astext.label('decision_id'),
            func.count(AnalyticsEvent.id).label('choice_count')
        ).filter(
            and_(
                AnalyticsEvent.timestamp >= time_range.start_date,
                AnalyticsEvent.timestamp <= time_range.end_date,
                AnalyticsEvent.event_type == 'decision_made'
            )
        ).group_by('decision_id').order_by(func.count(AnalyticsEvent.id).desc()).limit(10).all()
        
        return [
            {'decision_id': decision_id, 'choice_count': choice_count}
            for decision_id, choice_count in decisions
        ]
    
    def _get_drop_off_points(self, time_range: TimeRange) -> List[Dict[str, Any]]:
        """Get narrative drop-off points"""
        # This would require complex analysis of user progression
        # For now, return empty list
        return []
    
    def _get_experience_start_rate(self, time_range: TimeRange) -> float:
        """Get experience start rate"""
        # This would require tracking experience starts
        # For now, return a placeholder value
        return 0.45  # 45% start rate
    
    def _get_experience_completion_rate(self, time_range: TimeRange) -> float:
        """Get experience completion rate"""
        # This would require tracking experience completions
        # For now, return a placeholder value
        return 0.25  # 25% completion rate
    
    def _get_avg_experience_completion_time(self, time_range: TimeRange) -> float:
        """Get average experience completion time in seconds"""
        # This would require tracking experience timing
        # For now, return a placeholder value
        return 1200.0  # 20 minutes average
    
    def _get_popular_experiences(self, time_range: TimeRange) -> List[Dict[str, Any]]:
        """Get popular experiences"""
        
        experiences = self.db.query(
            AnalyticsEvent.metadata['experience_id'].astext.label('experience_id'),
            func.count(AnalyticsEvent.id).label('start_count')
        ).filter(
            and_(
                AnalyticsEvent.timestamp >= time_range.start_date,
                AnalyticsEvent.timestamp <= time_range.end_date,
                AnalyticsEvent.event_type == 'experience_started'
            )
        ).group_by('experience_id').order_by(func.count(AnalyticsEvent.id).desc()).limit(10).all()
        
        return [
            {'experience_id': experience_id, 'start_count': start_count}
            for experience_id, start_count in experiences
        ]