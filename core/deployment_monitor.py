"""
Post-Deployment Monitoring System

Monitors system health after deployments and triggers automatic rollbacks
if critical metrics exceed baseline thresholds.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from database.connection import get_db
from database.models import EventLog, UserBalance, User, Subscription
from core.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)


class DeploymentMonitor:
    """Monitors system health after deployments"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or next(get_db())
        self.feature_flags = FeatureFlags(self.db_session)
        self.baseline_metrics = self._load_baseline_metrics()
        self.alert_handlers = []
        self.rollback_handlers = []
    
    def post_deployment_monitoring(self, deployment_id: str, feature_name: str) -> Dict[str, Any]:
        """
        Monitor system health after a deployment
        
        Args:
            deployment_id: Unique identifier for this deployment
            feature_name: Name of the feature being deployed
            
        Returns:
            Dictionary with monitoring results and actions taken
        """
        try:
            logger.info(f"Starting post-deployment monitoring for {feature_name} (deployment: {deployment_id})")
            
            # Get metrics for the last 15 minutes
            metrics = self._get_current_metrics()
            
            # Check if metrics exceed baseline thresholds
            health_check = self._check_health_metrics(metrics)
            
            # Take action based on health check
            actions_taken = self._take_action(health_check, deployment_id, feature_name)
            
            result = {
                'deployment_id': deployment_id,
                'feature_name': feature_name,
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics,
                'health_check': health_check,
                'actions_taken': actions_taken,
                'status': 'healthy' if health_check['is_healthy'] else 'unhealthy'
            }
            
            logger.info(f"Post-deployment monitoring completed for {feature_name}: {result['status']}")
            return result
            
        except Exception as e:
            logger.error(f"Error in post-deployment monitoring for {deployment_id}: {e}")
            return {
                'deployment_id': deployment_id,
                'feature_name': feature_name,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status': 'error'
            }
    
    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        fifteen_minutes_ago = datetime.now() - timedelta(minutes=15)
        
        try:
            # Error rate
            total_events = self.db_session.query(func.count(EventLog.id)).filter(
                EventLog.created_at >= fifteen_minutes_ago
            ).scalar() or 1
            
            error_events = self.db_session.query(func.count(EventLog.id)).filter(
                and_(
                    EventLog.created_at >= fifteen_minutes_ago,
                    EventLog.event_type == 'error'
                )
            ).scalar() or 0
            
            error_rate = (error_events / total_events) * 100
            
            # Response time (simplified - would need actual timing data)
            # For now, we'll use a placeholder based on event processing
            avg_response_time = self._estimate_response_time()
            
            # User complaints (simplified - would integrate with support system)
            user_complaints = self._get_user_complaints(fifteen_minutes_ago)
            
            # System load metrics
            active_users = self.db_session.query(func.count(User.id)).filter(
                User.last_active >= fifteen_minutes_ago
            ).scalar() or 0
            
            # Revenue metrics
            revenue_data = self._get_revenue_metrics(fifteen_minutes_ago)
            
            return {
                'error_rate': error_rate,
                'avg_response_time': avg_response_time,
                'user_complaints': user_complaints,
                'active_users': active_users,
                'revenue': revenue_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            return {
                'error_rate': 0,
                'avg_response_time': 0,
                'user_complaints': 0,
                'active_users': 0,
                'revenue': {'total': 0, 'subscriptions': 0},
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _check_health_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Check if metrics exceed baseline thresholds"""
        baseline = self.baseline_metrics
        
        checks = {
            'error_rate': metrics['error_rate'] <= baseline['error_rate'] * 2,  # 2x baseline
            'response_time': metrics['avg_response_time'] <= baseline['response_time'] * 1.5,  # 1.5x baseline
            'user_complaints': metrics['user_complaints'] <= baseline['user_complaints'] * 3,  # 3x baseline
            'active_users': metrics['active_users'] >= baseline['active_users'] * 0.5,  # At least 50% of baseline
        }
        
        is_healthy = all(checks.values())
        
        return {
            'is_healthy': is_healthy,
            'checks': checks,
            'failed_checks': [k for k, v in checks.items() if not v],
            'baseline': baseline,
            'current': metrics
        }
    
    def _take_action(self, health_check: Dict[str, Any], deployment_id: str, feature_name: str) -> List[str]:
        """Take appropriate action based on health check results"""
        actions = []
        
        if not health_check['is_healthy']:
            logger.warning(f"Unhealthy deployment detected for {feature_name}: {health_check['failed_checks']}")
            
            # Trigger alerts
            self._trigger_alerts(deployment_id, feature_name, health_check)
            actions.append('alerts_triggered')
            
            # Check if we should trigger automatic rollback
            if self._should_trigger_rollback(health_check):
                rollback_success = self._trigger_rollback(feature_name)
                if rollback_success:
                    actions.append('rollback_triggered')
                    logger.info(f"Automatic rollback triggered for {feature_name}")
                else:
                    actions.append('rollback_failed')
                    logger.error(f"Failed to trigger rollback for {feature_name}")
        
        return actions
    
    def _should_trigger_rollback(self, health_check: Dict[str, Any]) -> bool:
        """Determine if automatic rollback should be triggered"""
        # Trigger rollback if error rate is more than 2x baseline
        if health_check['current']['error_rate'] > self.baseline_metrics['error_rate'] * 2:
            return True
        
        # Trigger rollback if multiple critical metrics are failing
        critical_failures = len([f for f in health_check['failed_checks'] 
                               if f in ['error_rate', 'response_time']])
        return critical_failures >= 2
    
    def _trigger_rollback(self, feature_name: str) -> bool:
        """Trigger automatic rollback for a feature"""
        try:
            # Disable the feature flag
            success = self.feature_flags.disable_feature(feature_name)
            
            # Call rollback handlers
            for handler in self.rollback_handlers:
                try:
                    handler(feature_name)
                except Exception as e:
                    logger.error(f"Error in rollback handler for {feature_name}: {e}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error triggering rollback for {feature_name}: {e}")
            return False
    
    def _trigger_alerts(self, deployment_id: str, feature_name: str, health_check: Dict[str, Any]) -> None:
        """Trigger alerts for unhealthy deployment"""
        alert_message = (
            f"🚨 UNHEALTHY DEPLOYMENT DETECTED\n"
            f"Deployment: {deployment_id}\n"
            f"Feature: {feature_name}\n"
            f"Failed checks: {', '.join(health_check['failed_checks'])}\n"
            f"Error rate: {health_check['current']['error_rate']:.2f}% (baseline: {health_check['baseline']['error_rate']:.2f}%)\n"
            f"Response time: {health_check['current']['avg_response_time']:.2f}s (baseline: {health_check['baseline']['response_time']:.2f}s)"
        )
        
        for handler in self.alert_handlers:
            try:
                handler(alert_message, deployment_id, feature_name, health_check)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
    
    def add_alert_handler(self, handler: Callable) -> None:
        """Add an alert handler function"""
        self.alert_handlers.append(handler)
    
    def add_rollback_handler(self, handler: Callable) -> None:
        """Add a rollback handler function"""
        self.rollback_handlers.append(handler)
    
    def _load_baseline_metrics(self) -> Dict[str, float]:
        """Load baseline metrics from historical data"""
        # In a real system, this would load from historical analytics
        # For now, using reasonable defaults
        return {
            'error_rate': 0.5,  # 0.5% error rate
            'response_time': 1.0,  # 1 second average response time
            'user_complaints': 5,  # 5 complaints per 15 minutes
            'active_users': 100,  # 100 active users per 15 minutes
        }
    
    def _estimate_response_time(self) -> float:
        """Estimate average response time (placeholder implementation)"""
        # In a real system, this would use actual timing data
        # For now, return a reasonable estimate
        return 0.8  # 800ms
    
    def _get_user_complaints(self, since: datetime) -> int:
        """Get number of user complaints since given time (placeholder)"""
        # In a real system, this would query support tickets
        # For now, return a placeholder value
        return 0
    
    def _get_revenue_metrics(self, since: datetime) -> Dict[str, float]:
        """Get revenue metrics since given time"""
        try:
            # Count active subscriptions
            active_subscriptions = self.db_session.query(func.count(Subscription.id)).filter(
                and_(
                    Subscription.status == 'active',
                    Subscription.created_at >= since
                )
            ).scalar() or 0
            
            # Calculate revenue (simplified)
            total_revenue = active_subscriptions * 5.0  # Assuming $5 per subscription
            
            return {
                'total': total_revenue,
                'subscriptions': active_subscriptions
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue metrics: {e}")
            return {'total': 0, 'subscriptions': 0}


# Global instance for easy access
deployment_monitor = DeploymentMonitor()