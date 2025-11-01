"""
Beta Tester Manager

Manages selection and management of beta testers for new features.
Supports different selection strategies based on user archetypes and activity.
"""

import logging
import random
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from database.connection import get_db
from database.models import User, UserBalance, EventLog, Subscription
from core.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)


class BetaTesterManager:
    """Manages beta tester selection and management"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or next(get_db())
        self.feature_flags = FeatureFlags(self.db_session)
    
    def select_beta_testers(
        self, 
        feature_name: str, 
        count: int = 20,
        strategy: str = 'balanced'
    ) -> List[int]:
        """
        Select beta testers for a feature
        
        Args:
            feature_name: Name of the feature
            count: Number of beta testers to select
            strategy: Selection strategy ('balanced', 'active', 'new', 'vip')
            
        Returns:
            List of user IDs selected as beta testers
        """
        try:
            logger.info(f"Selecting {count} beta testers for {feature_name} using {strategy} strategy")
            
            if strategy == 'balanced':
                testers = self._select_balanced_testers(count)
            elif strategy == 'active':
                testers = self._select_active_testers(count)
            elif strategy == 'new':
                testers = self._select_new_testers(count)
            elif strategy == 'vip':
                testers = self._select_vip_testers(count)
            else:
                logger.warning(f"Unknown strategy {strategy}, using balanced")
                testers = self._select_balanced_testers(count)
            
            # Add selected testers to the feature flag
            for user_id in testers:
                self.feature_flags.add_beta_tester(feature_name, user_id)
            
            logger.info(f"Selected {len(testers)} beta testers for {feature_name}")
            return testers
            
        except Exception as e:
            logger.error(f"Error selecting beta testers for {feature_name}: {e}")
            return []
    
    def get_beta_tester_candidates(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get potential beta tester candidates with their metrics"""
        try:
            # Get active users from the last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            # Query users with their activity metrics
            candidates = self.db_session.query(
                User.id,
                User.username,
                User.created_at,
                User.last_active,
                UserBalance.besitos,
                Subscription.status
            ).outerjoin(UserBalance, User.id == UserBalance.user_id).outerjoin(
                Subscription, and_(
                    Subscription.user_id == User.id,
                    Subscription.status == 'active'
                )
            ).filter(
                User.last_active >= thirty_days_ago
            ).order_by(desc(User.last_active)).limit(count).all()
            
            result = []
            for candidate in candidates:
                user_data = {
                    'user_id': candidate.id,
                    'username': candidate.username,
                    'created_at': candidate.created_at.isoformat() if candidate.created_at else None,
                    'last_active': candidate.last_active.isoformat() if candidate.last_active else None,
                    'besitos_balance': candidate.besitos or 0,
                    'is_vip': candidate.status == 'active',
                    'activity_score': self._calculate_activity_score(candidate.id),
                    'engagement_score': self._calculate_engagement_score(candidate.id)
                }
                result.append(user_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting beta tester candidates: {e}")
            return []
    
    def get_beta_tester_stats(self, feature_name: str) -> Dict[str, Any]:
        """Get statistics about beta testers for a feature"""
        try:
            beta_testers = self.feature_flags.get_beta_testers(feature_name)
            
            if not beta_testers:
                return {
                    'total_testers': 0,
                    'vip_testers': 0,
                    'new_testers': 0,
                    'active_testers': 0,
                    'average_activity_score': 0
                }
            
            # Get detailed information about beta testers
            testers_info = []
            vip_count = 0
            new_count = 0
            active_count = 0
            total_activity_score = 0
            
            for user_id in beta_testers:
                user_info = self._get_user_info(user_id)
                if user_info:
                    testers_info.append(user_info)
                    
                    if user_info.get('is_vip'):
                        vip_count += 1
                    
                    if user_info.get('is_new_user'):
                        new_count += 1
                    
                    if user_info.get('is_active'):
                        active_count += 1
                    
                    total_activity_score += user_info.get('activity_score', 0)
            
            return {
                'total_testers': len(beta_testers),
                'vip_testers': vip_count,
                'new_testers': new_count,
                'active_testers': active_count,
                'average_activity_score': total_activity_score / len(beta_testers) if beta_testers else 0,
                'testers': testers_info
            }
            
        except Exception as e:
            logger.error(f"Error getting beta tester stats for {feature_name}: {e}")
            return {}
    
    def remove_beta_tester(self, feature_name: str, user_id: int) -> bool:
        """Remove a user from beta testers for a feature"""
        return self.feature_flags.remove_beta_tester(feature_name, user_id)
    
    def clear_beta_testers(self, feature_name: str) -> bool:
        """Clear all beta testers for a feature"""
        try:
            beta_testers = self.feature_flags.get_beta_testers(feature_name)
            
            for user_id in beta_testers:
                self.feature_flags.remove_beta_tester(feature_name, user_id)
            
            logger.info(f"Cleared all beta testers for {feature_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing beta testers for {feature_name}: {e}")
            return False
    
    def _select_balanced_testers(self, count: int) -> List[int]:
        """Select a balanced mix of user types"""
        testers = []
        
        # Get candidates from different categories
        vip_candidates = self._get_vip_candidates(count // 3)
        active_candidates = self._get_active_candidates(count // 3)
        new_candidates = self._get_new_candidates(count // 3)
        
        # Combine and deduplicate
        all_candidates = list(set(vip_candidates + active_candidates + new_candidates))
        
        # If we don't have enough candidates, fill with random active users
        if len(all_candidates) < count:
            additional = self._get_random_active_candidates(count - len(all_candidates))
            all_candidates.extend(additional)
        
        # Randomly select the final testers
        testers = random.sample(all_candidates, min(count, len(all_candidates)))
        
        return testers
    
    def _select_active_testers(self, count: int) -> List[int]:
        """Select the most active users"""
        return self._get_active_candidates(count)
    
    def _select_new_testers(self, count: int) -> List[int]:
        """Select recently joined users"""
        return self._get_new_candidates(count)
    
    def _select_vip_testers(self, count: int) -> List[int]:
        """Select VIP users"""
        return self._get_vip_candidates(count)
    
    def _get_vip_candidates(self, count: int) -> List[int]:
        """Get VIP user candidates"""
        try:
            vip_users = self.db_session.query(User.id).join(
                Subscription, and_(
                    Subscription.user_id == User.id,
                    Subscription.status == 'active'
                )
            ).order_by(desc(User.last_active)).limit(count).all()
            
            return [user.id for user in vip_users]
            
        except Exception as e:
            logger.error(f"Error getting VIP candidates: {e}")
            return []
    
    def _get_active_candidates(self, count: int) -> List[int]:
        """Get active user candidates"""
        try:
            seven_days_ago = datetime.now() - timedelta(days=7)
            
            active_users = self.db_session.query(User.id).filter(
                User.last_active >= seven_days_ago
            ).order_by(desc(User.last_active)).limit(count).all()
            
            return [user.id for user in active_users]
            
        except Exception as e:
            logger.error(f"Error getting active candidates: {e}")
            return []
    
    def _get_new_candidates(self, count: int) -> List[int]:
        """Get new user candidates"""
        try:
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            new_users = self.db_session.query(User.id).filter(
                User.created_at >= thirty_days_ago
            ).order_by(desc(User.created_at)).limit(count).all()
            
            return [user.id for user in new_users]
            
        except Exception as e:
            logger.error(f"Error getting new candidates: {e}")
            return []
    
    def _get_random_active_candidates(self, count: int) -> List[int]:
        """Get random active user candidates"""
        try:
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            active_users = self.db_session.query(User.id).filter(
                User.last_active >= thirty_days_ago
            ).all()
            
            if not active_users:
                return []
            
            return random.sample([user.id for user in active_users], min(count, len(active_users)))
            
        except Exception as e:
            logger.error(f"Error getting random active candidates: {e}")
            return []
    
    def _calculate_activity_score(self, user_id: int) -> float:
        """Calculate activity score for a user (0-100)"""
        try:
            seven_days_ago = datetime.now() - timedelta(days=7)
            
            # Count events in the last 7 days
            event_count = self.db_session.query(func.count(EventLog.id)).filter(
                and_(
                    EventLog.user_id == user_id,
                    EventLog.created_at >= seven_days_ago
                )
            ).scalar() or 0
            
            # Normalize to 0-100 scale (assuming 50+ events is max activity)
            return min(event_count * 2, 100)
            
        except Exception as e:
            logger.error(f"Error calculating activity score for user {user_id}: {e}")
            return 0
    
    def _calculate_engagement_score(self, user_id: int) -> float:
        """Calculate engagement score for a user (0-100)"""
        try:
            # Simple engagement score based on multiple factors
            activity_score = self._calculate_activity_score(user_id)
            
            # Check if user has besitos balance
            balance = self.db_session.query(UserBalance.besitos).filter(
                UserBalance.user_id == user_id
            ).scalar() or 0
            
            # Check if user is VIP
            is_vip = self.db_session.query(Subscription.id).filter(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.status == 'active'
                )
            ).first() is not None
            
            # Calculate engagement score
            engagement_score = activity_score * 0.6  # 60% weight on activity
            engagement_score += (min(balance / 100, 1) * 20)  # 20% weight on balance
            engagement_score += (20 if is_vip else 0)  # 20% weight on VIP status
            
            return min(engagement_score, 100)
            
        except Exception as e:
            logger.error(f"Error calculating engagement score for user {user_id}: {e}")
            return 0
    
    def _get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a user"""
        try:
            user = self.db_session.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            balance = self.db_session.query(UserBalance.besitos).filter(
                UserBalance.user_id == user_id
            ).scalar() or 0
            
            is_vip = self.db_session.query(Subscription.id).filter(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.status == 'active'
                )
            ).first() is not None
            
            # Check if user is new (joined in last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            is_new_user = user.created_at >= thirty_days_ago if user.created_at else False
            
            # Check if user is active (active in last 7 days)
            seven_days_ago = datetime.now() - timedelta(days=7)
            is_active = user.last_active >= seven_days_ago if user.last_active else False
            
            return {
                'user_id': user_id,
                'username': user.username,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_active': user.last_active.isoformat() if user.last_active else None,
                'besitos_balance': balance,
                'is_vip': is_vip,
                'is_new_user': is_new_user,
                'is_active': is_active,
                'activity_score': self._calculate_activity_score(user_id),
                'engagement_score': self._calculate_engagement_score(user_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting user info for {user_id}: {e}")
            return None


# Global instance for easy access
beta_tester_manager = BetaTesterManager()