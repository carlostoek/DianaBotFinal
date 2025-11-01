"""
Economy Monitoring System

Monitors the health and balance of the besitos economy system.
Tracks faucets (sources) and sinks (spending) to detect inflation/deflation.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case

from database.connection import get_db
from database.models import Transaction, UserBalance, User

logger = logging.getLogger(__name__)


class EconomyMonitor:
    """Monitors the health and balance of the besitos economy"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or next(get_db())
        self.baseline_metrics = self._load_baseline_metrics()
        self.alert_handlers = []
    
    def monitor_economy_health(self) -> Dict[str, Any]:
        """
        Monitor the overall health of the besitos economy
        
        Returns:
            Dictionary with economy health metrics and alerts
        """
        try:
            logger.info("Starting economy health monitoring")
            
            # Get economy metrics for the last 24 hours
            metrics = self._get_economy_metrics()
            
            # Check for economic imbalances
            health_check = self._check_economy_health(metrics)
            
            # Generate alerts if needed
            alerts = self._generate_alerts(health_check)
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics,
                'health_check': health_check,
                'alerts': alerts,
                'status': 'healthy' if health_check['is_healthy'] else 'unhealthy'
            }
            
            logger.info(f"Economy health monitoring completed: {result['status']}")
            return result
            
        except Exception as e:
            logger.error(f"Error in economy health monitoring: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status': 'error'
            }
    
    def _get_economy_metrics(self) -> Dict[str, Any]:
        """Get comprehensive economy metrics"""
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        
        try:
            # Total besitos in circulation
            total_besitos = self.db_session.query(func.sum(UserBalance.besitos)).scalar() or 0
            
            # Total lifetime besitos earned
            total_lifetime_besitos = self.db_session.query(func.sum(UserBalance.lifetime_besitos)).scalar() or 0
            
            # Faucets (sources) - besitos entering the economy
            faucets = self._get_faucet_metrics(twenty_four_hours_ago)
            
            # Sinks (spending) - besitos leaving the economy
            sinks = self._get_sink_metrics(twenty_four_hours_ago)
            
            # Velocity metrics
            velocity = self._get_velocity_metrics(twenty_four_hours_ago)
            
            # User distribution metrics
            user_distribution = self._get_user_distribution_metrics()
            
            return {
                'total_besitos': total_besitos,
                'total_lifetime_besitos': total_lifetime_besitos,
                'faucets': faucets,
                'sinks': sinks,
                'velocity': velocity,
                'user_distribution': user_distribution,
                'net_flow': faucets['total'] - sinks['total'],
                'inflation_rate': self._calculate_inflation_rate(faucets['total'], sinks['total']),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting economy metrics: {e}")
            return {
                'total_besitos': 0,
                'total_lifetime_besitos': 0,
                'faucets': {'total': 0, 'breakdown': {}},
                'sinks': {'total': 0, 'breakdown': {}},
                'velocity': {'avg_transactions_per_user': 0, 'avg_besitos_per_transaction': 0},
                'user_distribution': {},
                'net_flow': 0,
                'inflation_rate': 0,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _get_faucet_metrics(self, since: datetime) -> Dict[str, Any]:
        """Get metrics for besitos faucets (sources)"""
        try:
            # Query transactions where besitos are earned
            faucet_query = self.db_session.query(
                Transaction.source,
                func.sum(Transaction.amount).label('total_amount'),
                func.count(Transaction.id).label('transaction_count')
            ).filter(
                and_(
                    Transaction.created_at >= since,
                    Transaction.transaction_type == 'earn'
                )
            ).group_by(Transaction.source)
            
            faucet_results = faucet_query.all()
            
            breakdown = {}
            total_faucets = 0
            
            for source, amount, count in faucet_results:
                breakdown[source] = {
                    'amount': amount,
                    'transaction_count': count,
                    'avg_amount_per_transaction': amount / count if count > 0 else 0
                }
                total_faucets += amount
            
            return {
                'total': total_faucets,
                'breakdown': breakdown
            }
            
        except Exception as e:
            logger.error(f"Error getting faucet metrics: {e}")
            return {'total': 0, 'breakdown': {}}
    
    def _get_sink_metrics(self, since: datetime) -> Dict[str, Any]:
        """Get metrics for besitos sinks (spending)"""
        try:
            # Query transactions where besitos are spent
            sink_query = self.db_session.query(
                Transaction.source,
                func.sum(Transaction.amount).label('total_amount'),
                func.count(Transaction.id).label('transaction_count')
            ).filter(
                and_(
                    Transaction.created_at >= since,
                    Transaction.transaction_type == 'spend'
                )
            ).group_by(Transaction.source)
            
            sink_results = sink_query.all()
            
            breakdown = {}
            total_sinks = 0
            
            for source, amount, count in sink_results:
                breakdown[source] = {
                    'amount': amount,
                    'transaction_count': count,
                    'avg_amount_per_transaction': amount / count if count > 0 else 0
                }
                total_sinks += amount
            
            return {
                'total': total_sinks,
                'breakdown': breakdown
            }
            
        except Exception as e:
            logger.error(f"Error getting sink metrics: {e}")
            return {'total': 0, 'breakdown': {}}
    
    def _get_velocity_metrics(self, since: datetime) -> Dict[str, float]:
        """Get velocity metrics for the economy"""
        try:
            # Average transactions per user
            user_transaction_counts = self.db_session.query(
                Transaction.user_id,
                func.count(Transaction.id).label('transaction_count')
            ).filter(
                Transaction.created_at >= since
            ).group_by(Transaction.user_id).subquery()
            
            avg_transactions_per_user = self.db_session.query(
                func.avg(user_transaction_counts.c.transaction_count)
            ).scalar() or 0
            
            # Average besitos per transaction
            avg_besitos_per_transaction = self.db_session.query(
                func.avg(Transaction.amount)
            ).filter(
                Transaction.created_at >= since
            ).scalar() or 0
            
            return {
                'avg_transactions_per_user': float(avg_transactions_per_user),
                'avg_besitos_per_transaction': float(avg_besitos_per_transaction)
            }
            
        except Exception as e:
            logger.error(f"Error getting velocity metrics: {e}")
            return {'avg_transactions_per_user': 0, 'avg_besitos_per_transaction': 0}
    
    def _get_user_distribution_metrics(self) -> Dict[str, Any]:
        """Get user distribution metrics for besitos"""
        try:
            # Get user balances
            balances = self.db_session.query(UserBalance.besitos).all()
            balance_values = [b[0] for b in balances if b[0] is not None]
            
            if not balance_values:
                return {}
            
            # Calculate distribution metrics
            total_users = len(balance_values)
            avg_balance = sum(balance_values) / total_users
            max_balance = max(balance_values)
            min_balance = min(balance_values)
            
            # Calculate percentiles
            sorted_balances = sorted(balance_values)
            median_balance = sorted_balances[len(sorted_balances) // 2]
            p90_balance = sorted_balances[int(len(sorted_balances) * 0.9)]
            p95_balance = sorted_balances[int(len(sorted_balances) * 0.95)]
            
            # Gini coefficient (simplified)
            gini = self._calculate_gini_coefficient(balance_values)
            
            return {
                'total_users': total_users,
                'avg_balance': avg_balance,
                'median_balance': median_balance,
                'max_balance': max_balance,
                'min_balance': min_balance,
                'p90_balance': p90_balance,
                'p95_balance': p95_balance,
                'gini_coefficient': gini,
                'wealth_inequality': 'high' if gini > 0.6 else 'moderate' if gini > 0.4 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error getting user distribution metrics: {e}")
            return {}
    
    def _check_economy_health(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Check if economy metrics indicate healthy balance"""
        baseline = self.baseline_metrics
        
        checks = {
            'inflation_under_control': metrics['inflation_rate'] <= baseline['max_inflation_rate'],
            'faucets_sinks_balanced': abs(metrics['net_flow']) <= baseline['max_net_flow'],
            'velocity_healthy': metrics['velocity']['avg_transactions_per_user'] >= baseline['min_velocity'],
            'wealth_inequality_acceptable': metrics['user_distribution'].get('gini_coefficient', 0) <= baseline['max_gini_coefficient'],
            'sufficient_circulation': metrics['total_besitos'] >= baseline['min_total_besitos']
        }
        
        is_healthy = all(checks.values())
        
        return {
            'is_healthy': is_healthy,
            'checks': checks,
            'failed_checks': [k for k, v in checks.items() if not v],
            'baseline': baseline,
            'current': metrics
        }
    
    def _generate_alerts(self, health_check: Dict[str, Any]) -> List[str]:
        """Generate alerts for economic imbalances"""
        alerts = []
        
        if not health_check['is_healthy']:
            for failed_check in health_check['failed_checks']:
                if failed_check == 'inflation_under_control':
                    alerts.append(f"High inflation detected: {health_check['current']['inflation_rate']:.2f}%")
                elif failed_check == 'faucets_sinks_balanced':
                    net_flow = health_check['current']['net_flow']
                    if net_flow > 0:
                        alerts.append(f"Economy inflation: {net_flow} besitos entering without sinks")
                    else:
                        alerts.append(f"Economy deflation: {abs(net_flow)} besitos leaving without faucets")
                elif failed_check == 'velocity_healthy':
                    alerts.append(f"Low economic velocity: {health_check['current']['velocity']['avg_transactions_per_user']:.2f} transactions/user")
                elif failed_check == 'wealth_inequality_acceptable':
                    gini = health_check['current']['user_distribution'].get('gini_coefficient', 0)
                    alerts.append(f"High wealth inequality: Gini coefficient {gini:.3f}")
                elif failed_check == 'sufficient_circulation':
                    alerts.append(f"Low besitos circulation: {health_check['current']['total_besitos']} total besitos")
        
        # Trigger alert handlers
        if alerts:
            for handler in self.alert_handlers:
                try:
                    handler(alerts, health_check)
                except Exception as e:
                    logger.error(f"Error in alert handler: {e}")
        
        return alerts
    
    def add_alert_handler(self, handler) -> None:
        """Add an alert handler function"""
        self.alert_handlers.append(handler)
    
    def _load_baseline_metrics(self) -> Dict[str, float]:
        """Load baseline metrics for economy health"""
        # In a real system, these would be calculated from historical data
        return {
            'max_inflation_rate': 10.0,  # Maximum acceptable inflation rate (%)
            'max_net_flow': 1000,  # Maximum acceptable net flow imbalance
            'min_velocity': 0.5,  # Minimum average transactions per user
            'max_gini_coefficient': 0.6,  # Maximum acceptable wealth inequality
            'min_total_besitos': 10000,  # Minimum total besitos in circulation
        }
    
    def _calculate_inflation_rate(self, faucets: int, sinks: int) -> float:
        """Calculate inflation rate based on faucets and sinks"""
        if sinks == 0:
            return 100.0  # Infinite inflation if no sinks
        
        return ((faucets - sinks) / sinks) * 100
    
    def _calculate_gini_coefficient(self, values: List[float]) -> float:
        """Calculate Gini coefficient for wealth inequality"""
        if not values:
            return 0.0
        
        # Sort values
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        # Calculate Gini coefficient
        total = sum(sorted_values)
        if total == 0:
            return 0.0
        
        cumulative_sum = 0
        for i, value in enumerate(sorted_values):
            cumulative_sum += (i + 1) * value
        
        gini = (2 * cumulative_sum) / (n * total) - (n + 1) / n
        return gini


# Global instance for easy access
economy_monitor = EconomyMonitor()