"""
Alert System for DianaBot Analytics System
Detects anomalies and sends notifications to admins
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from sqlalchemy import func, and_, or_, text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str
    alert_type: str
    severity: str  # low, medium, high, critical
    title: str
    description: str
    data: Dict[str, Any]
    detected_at: datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


@dataclass
class AlertConfig:
    """Alert configuration"""
    alert_type: str
    enabled: bool
    threshold: float
    comparison: str  # "greater_than", "less_than", "equal"
    time_window_hours: int
    notification_channels: List[str]  # "telegram", "email", "dashboard"


class AlertSystem:
    """Detects anomalies and sends notifications to admins"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.alert_configs = self._load_alert_configs()
    
    def check_anomalies(self) -> List[Alert]:
        """Check for all types of anomalies and return alerts"""
        logger.info("Checking for anomalies across all systems")
        
        alerts = []
        
        # Check engagement anomalies
        engagement_alerts = self._check_engagement_anomalies()
        alerts.extend(engagement_alerts)
        
        # Check monetization anomalies
        monetization_alerts = self._check_monetization_anomalies()
        alerts.extend(monetization_alerts)
        
        # Check technical anomalies
        technical_alerts = self._check_technical_anomalies()
        alerts.extend(technical_alerts)
        
        # Check content anomalies
        content_alerts = self._check_content_anomalies()
        alerts.extend(content_alerts)
        
        # Check user behavior anomalies
        user_alerts = self._check_user_anomalies()
        alerts.extend(user_alerts)
        
        # Send notifications for critical alerts
        for alert in alerts:
            if alert.severity in ['high', 'critical']:
                self._notify_admin(alert)
        
        return alerts
    
    def notify_admin(self, alert: Alert) -> bool:
        """Send notification to admin via configured channels"""
        logger.info(f"Sending admin notification for alert: {alert.alert_type}")
        
        config = self.alert_configs.get(alert.alert_type)
        if not config or not config.enabled:
            logger.warning(f"Alert type {alert.alert_type} is disabled or not configured")
            return False
        
        success = True
        
        # Send via Telegram
        if 'telegram' in config.notification_channels:
            success = success and self._send_telegram_notification(alert)
        
        # Send via Email
        if 'email' in config.notification_channels:
            success = success and self._send_email_notification(alert)
        
        # Send to Dashboard
        if 'dashboard' in config.notification_channels:
            success = success and self._send_dashboard_notification(alert)
        
        return success
    
    def get_alert_config(self, alert_type: str) -> Optional[AlertConfig]:
        """Get configuration for specific alert type"""
        return self.alert_configs.get(alert_type)
    
    def update_alert_config(self, alert_type: str, config: AlertConfig) -> bool:
        """Update configuration for alert type"""
        self.alert_configs[alert_type] = config
        return True
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Mark alert as acknowledged"""
        # In production, this would update the alert in database
        logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
        return True
    
    # Private helper methods
    
    def _load_alert_configs(self) -> Dict[str, AlertConfig]:
        """Load alert configurations"""
        return {
            'engagement_drop': AlertConfig(
                alert_type='engagement_drop',
                enabled=True,
                threshold=0.2,  # 20% drop
                comparison='less_than',
                time_window_hours=24,
                notification_channels=['telegram', 'dashboard']
            ),
            'conversion_drop': AlertConfig(
                alert_type='conversion_drop',
                enabled=True,
                threshold=0.15,  # 15% drop
                comparison='less_than',
                time_window_hours=24,
                notification_channels=['telegram', 'email', 'dashboard']
            ),
            'technical_errors': AlertConfig(
                alert_type='technical_errors',
                enabled=True,
                threshold=10,  # 10 errors
                comparison='greater_than',
                time_window_hours=1,
                notification_channels=['telegram', 'email']
            ),
            'high_value_user_risk': AlertConfig(
                alert_type='high_value_user_risk',
                enabled=True,
                threshold=0.7,  # 70% probability
                comparison='greater_than',
                time_window_hours=24,
                notification_channels=['dashboard']
            ),
            'besitos_economy_anomaly': AlertConfig(
                alert_type='besitos_economy_anomaly',
                enabled=True,
                threshold=0.3,  # 30% deviation
                comparison='greater_than',
                time_window_hours=24,
                notification_channels=['dashboard']
            )
        }
    
    def _check_engagement_anomalies(self) -> List[Alert]:
        """Check for engagement anomalies"""
        alerts = []
        
        # Check DAU drop
        current_dau = self._get_current_dau()
        previous_dau = self._get_previous_dau()
        
        if previous_dau > 0:
            drop_percentage = (previous_dau - current_dau) / previous_dau
            
            if drop_percentage > 0.2:  # More than 20% drop
                alerts.append(Alert(
                    alert_id=f"engagement_drop_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    alert_type='engagement_drop',
                    severity='high',
                    title="Significant Drop in Daily Active Users",
                    description=f"DAU dropped by {drop_percentage:.1%} compared to previous period",
                    data={
                        'current_dau': current_dau,
                        'previous_dau': previous_dau,
                        'drop_percentage': drop_percentage
                    },
                    detected_at=datetime.now()
                ))
        
        # Check session duration drop
        current_session_duration = self._get_current_session_duration()
        previous_session_duration = self._get_previous_session_duration()
        
        if previous_session_duration > 0:
            drop_percentage = (previous_session_duration - current_session_duration) / previous_session_duration
            
            if drop_percentage > 0.3:  # More than 30% drop
                alerts.append(Alert(
                    alert_id=f"session_duration_drop_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    alert_type='engagement_drop',
                    severity='medium',
                    title="Drop in Average Session Duration",
                    description=f"Average session duration dropped by {drop_percentage:.1%}",
                    data={
                        'current_duration': current_session_duration,
                        'previous_duration': previous_session_duration,
                        'drop_percentage': drop_percentage
                    },
                    detected_at=datetime.now()
                ))
        
        return alerts
    
    def _check_monetization_anomalies(self) -> List[Alert]:
        """Check for monetization anomalies"""
        alerts = []
        
        # Check conversion rate drop
        current_conversion = self._get_current_conversion_rate()
        previous_conversion = self._get_previous_conversion_rate()
        
        if previous_conversion > 0:
            drop_percentage = (previous_conversion - current_conversion) / previous_conversion
            
            if drop_percentage > 0.15:  # More than 15% drop
                alerts.append(Alert(
                    alert_id=f"conversion_drop_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    alert_type='conversion_drop',
                    severity='high',
                    title="Drop in Conversion Rate",
                    description=f"Conversion rate dropped by {drop_percentage:.1%}",
                    data={
                        'current_conversion': current_conversion,
                        'previous_conversion': previous_conversion,
                        'drop_percentage': drop_percentage
                    },
                    detected_at=datetime.now()
                ))
        
        # Check revenue anomalies
        current_revenue = self._get_current_revenue()
        previous_revenue = self._get_previous_revenue()
        
        if previous_revenue > 0:
            drop_percentage = (previous_revenue - current_revenue) / previous_revenue
            
            if drop_percentage > 0.25:  # More than 25% drop
                alerts.append(Alert(
                    alert_id=f"revenue_drop_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    alert_type='conversion_drop',
                    severity='critical',
                    title="Significant Revenue Drop",
                    description=f"Revenue dropped by {drop_percentage:.1%}",
                    data={
                        'current_revenue': current_revenue,
                        'previous_revenue': previous_revenue,
                        'drop_percentage': drop_percentage
                    },
                    detected_at=datetime.now()
                ))
        
        return alerts
    
    def _check_technical_anomalies(self) -> List[Alert]:
        """Check for technical anomalies"""
        alerts = []
        
        # Check error rate
        error_count = self._get_recent_error_count()
        
        if error_count > 10:  # More than 10 errors in last hour
            alerts.append(Alert(
                alert_id=f"technical_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                alert_type='technical_errors',
                severity='critical',
                title="High Error Rate Detected",
                description=f"{error_count} errors detected in the last hour",
                data={'error_count': error_count},
                detected_at=datetime.now()
            ))
        
        # Check system performance
        avg_response_time = self._get_avg_response_time()
        
        if avg_response_time > 5000:  # More than 5 seconds
            alerts.append(Alert(
                alert_id=f"performance_issue_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                alert_type='technical_errors',
                severity='medium',
                title="Performance Degradation",
                description=f"Average response time is {avg_response_time}ms",
                data={'avg_response_time': avg_response_time},
                detected_at=datetime.now()
            ))
        
        return alerts
    
    def _check_content_anomalies(self) -> List[Alert]:
        """Check for content-related anomalies"""
        alerts = []
        
        # Check for content with unusually low engagement
        low_engagement_content = self._get_low_engagement_content()
        
        if low_engagement_content:
            alerts.append(Alert(
                alert_id=f"content_engagement_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                alert_type='content_anomaly',
                severity='low',
                title="Content with Low Engagement",
                description=f"{len(low_engagement_content)} content items have below-average engagement",
                data={'low_engagement_content': low_engagement_content},
                detected_at=datetime.now()
            ))
        
        return alerts
    
    def _check_user_anomalies(self) -> List[Alert]:
        """Check for user behavior anomalies"""
        alerts = []
        
        # Check for high-value users at risk
        at_risk_users = self._get_high_value_users_at_risk()
        
        if at_risk_users:
            alerts.append(Alert(
                alert_id=f"high_value_risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                alert_type='high_value_user_risk',
                severity='medium',
                title="High-Value Users at Risk",
                description=f"{len(at_risk_users)} high-value users showing signs of churn",
                data={'at_risk_users': at_risk_users},
                detected_at=datetime.now()
            ))
        
        return alerts
    
    def _notify_admin(self, alert: Alert) -> bool:
        """Internal method to send admin notifications"""
        return self.notify_admin(alert)
    
    def _send_telegram_notification(self, alert: Alert) -> bool:
        """Send notification via Telegram"""
        # In production, this would integrate with Telegram Bot API
        logger.info(f"[TELEGRAM] {alert.severity.upper()}: {alert.title} - {alert.description}")
        return True
    
    def _send_email_notification(self, alert: Alert) -> bool:
        """Send notification via Email"""
        # In production, this would integrate with email service
        logger.info(f"[EMAIL] {alert.severity.upper()}: {alert.title} - {alert.description}")
        return True
    
    def _send_dashboard_notification(self, alert: Alert) -> bool:
        """Send notification to dashboard"""
        # In production, this would update dashboard state
        logger.info(f"[DASHBOARD] {alert.severity.upper()}: {alert.title} - {alert.description}")
        return True
    
    # Data access methods (simplified implementations)
    
    def _get_current_dau(self) -> int:
        """Get current daily active users"""
        from database.models import AnalyticsEvent
        
        today = datetime.now().date()
        result = self.db.query(func.count(func.distinct(AnalyticsEvent.user_id))).filter(
            func.date(AnalyticsEvent.timestamp) == today
        ).scalar()
        
        return result or 0
    
    def _get_previous_dau(self) -> int:
        """Get previous day's active users"""
        from database.models import AnalyticsEvent
        
        yesterday = (datetime.now() - timedelta(days=1)).date()
        result = self.db.query(func.count(func.distinct(AnalyticsEvent.user_id))).filter(
            func.date(AnalyticsEvent.timestamp) == yesterday
        ).scalar()
        
        return result or 0
    
    def _get_current_session_duration(self) -> float:
        """Get current average session duration"""
        # Placeholder implementation
        return 300.0  # 5 minutes
    
    def _get_previous_session_duration(self) -> float:
        """Get previous average session duration"""
        # Placeholder implementation
        return 350.0  # 5.8 minutes
    
    def _get_current_conversion_rate(self) -> float:
        """Get current conversion rate"""
        # Placeholder implementation
        return 0.05  # 5%
    
    def _get_previous_conversion_rate(self) -> float:
        """Get previous conversion rate"""
        # Placeholder implementation
        return 0.06  # 6%
    
    def _get_current_revenue(self) -> float:
        """Get current revenue"""
        from database.models import Transaction
        
        today = datetime.now().date()
        result = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                func.date(Transaction.created_at) == today,
                Transaction.status == 'completed'
            )
        ).scalar()
        
        return float(result or 0)
    
    def _get_previous_revenue(self) -> float:
        """Get previous day's revenue"""
        from database.models import Transaction
        
        yesterday = (datetime.now() - timedelta(days=1)).date()
        result = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                func.date(Transaction.created_at) == yesterday,
                Transaction.status == 'completed'
            )
        ).scalar()
        
        return float(result or 0)
    
    def _get_recent_error_count(self) -> int:
        """Get recent error count"""
        from database.models import AnalyticsEvent
        
        one_hour_ago = datetime.now() - timedelta(hours=1)
        result = self.db.query(func.count(AnalyticsEvent.id)).filter(
            and_(
                AnalyticsEvent.timestamp >= one_hour_ago,
                AnalyticsEvent.event_type == 'error'
            )
        ).scalar()
        
        return result or 0
    
    def _get_avg_response_time(self) -> float:
        """Get average response time"""
        # Placeholder implementation
        return 1200.0  # 1.2 seconds
    
    def _get_low_engagement_content(self) -> List[Dict[str, Any]]:
        """Get content with low engagement"""
        # Placeholder implementation
        return []
    
    def _get_high_value_users_at_risk(self) -> List[Dict[str, Any]]:
        """Get high-value users at risk of churn"""
        # Placeholder implementation
        return []