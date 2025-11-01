#!/usr/bin/env python3
"""
Subscription Lifecycle Management
Manages automated subscription workflows, conversion funnels, and lifecycle events
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from enum import Enum
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Subscription, User
from modules.commerce.archetypes import ArchetypeEngine
from core.event_bus import event_bus
from core.coordinator import CoordinadorCentral

logger = logging.getLogger(__name__)


class SubscriptionStage(Enum):
    """Subscription lifecycle stages"""
    FREE_TRIAL = "free_trial"
    ENGAGEMENT = "engagement"
    CONSIDERATION = "consideration"
    CONVERSION = "conversion"
    ACTIVE_VIP = "active_vip"
    RENEWAL = "renewal"
    CHURN_RISK = "churn_risk"
    EXPIRED = "expired"


class SubscriptionLifecycle:
    """Manages subscription lifecycle and conversion funnels"""
    
    def __init__(self, db: Session):
        self.db: Session = db
        self.archetype_engine = ArchetypeEngine(self.db)
        self.event_bus = event_bus
        self.coordinator = CoordinadorCentral(event_bus)
    
    def start_conversion_funnel(self, user_id: int, funnel_type: str, initial_stage: str) -> bool:
        """
        Start tracking a user's conversion journey
        
        Args:
            user_id: User ID
            funnel_type: Type of funnel ('free_to_vip', 'engagement_to_purchase', 'free_to_purchaser')
            initial_stage: Initial stage of the funnel
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Import ConversionFunnel from main models
            from database.models import ConversionFunnel
            
            # Check if user already has an active funnel of this type
            existing_funnel = self.db.query(ConversionFunnel).filter(
                ConversionFunnel.user_id == user_id,
                ConversionFunnel.funnel_type == funnel_type,
                ConversionFunnel.is_active == True
            ).first()
            
            if existing_funnel:
                logger.info(f"User {user_id} already has active {funnel_type} funnel")
                return True
            
            # Create new conversion funnel
            funnel = ConversionFunnel(
                user_id=user_id,
                funnel_type=funnel_type,
                stage_entered=initial_stage,
                stage_current=initial_stage,
                stage_completed=None,
                is_active=True,
                is_completed=False,
                funnel_data={
                    "touchpoints": 0,
                    "offers_shown": 0,
                    "offers_clicked": 0,
                    "barriers_encountered": [],
                    "time_to_convert": None,
                    "conversion_value": None
                }
            )
            
            self.db.add(funnel)
            self.db.commit()
            
            # Emit event
            self.event_bus.publish(
                "conversion_funnel_started",
                {
                    "user_id": user_id,
                    "funnel_type": funnel_type,
                    "initial_stage": initial_stage,
                    "funnel_id": funnel.id
                }
            )
            
            logger.info(f"Started {funnel_type} conversion funnel for user {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to start conversion funnel for user {user_id}: {e}")
            return False
    
    def update_conversion_stage(self, funnel_id: int, new_stage: str, metadata: Optional[Dict] = None) -> bool:
        """
        Update user's current stage in conversion funnel
        
        Args:
            funnel_id: Conversion funnel ID
            new_stage: New stage to transition to
            metadata: Additional metadata for the stage transition
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from database.models import ConversionFunnel
            
            funnel = self.db.query(ConversionFunnel).filter(
                ConversionFunnel.id == funnel_id
            ).first()
            
            if not funnel:
                logger.warning(f"Conversion funnel {funnel_id} not found")
                return False
            
            # Update stage
            funnel.stage_current = new_stage
            funnel.last_activity_at = datetime.now()
            
            # Update metadata
            if metadata:
                if not funnel.funnel_data:
                    funnel.funnel_data = {}
                funnel.funnel_data.update(metadata)
            
            # Track touchpoints
            if funnel.funnel_data and "touchpoints" in funnel.funnel_data:
                funnel.funnel_data["touchpoints"] += 1
            
            self.db.commit()
            
            # Emit event
            self.event_bus.publish(
                "conversion_stage_updated",
                {
                    "funnel_id": funnel_id,
                    "user_id": funnel.user_id,
                    "old_stage": funnel.stage_entered,
                    "new_stage": new_stage,
                    "funnel_type": funnel.funnel_type
                }
            )
            
            logger.info(f"Updated conversion funnel {funnel_id} to stage {new_stage}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update conversion stage for funnel {funnel_id}: {e}")
            return False
    
    def complete_conversion_funnel(self, funnel_id: int, final_stage: str, conversion_data: Dict) -> bool:
        """
        Mark conversion funnel as completed
        
        Args:
            funnel_id: Conversion funnel ID
            final_stage: Final stage reached
            conversion_data: Data about the conversion
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from database.models import ConversionFunnel
            from sqlalchemy.sql import func
            
            funnel = self.db.query(ConversionFunnel).filter(
                ConversionFunnel.id == funnel_id
            ).first()
            
            if not funnel:
                logger.warning(f"Conversion funnel {funnel_id} not found")
                return False
            
            # Calculate time to convert - handle timezone mismatch
            current_time = datetime.now(timezone.utc)
            time_to_convert = (current_time - funnel.entered_at).total_seconds()
            
            # Update funnel
            funnel.stage_completed = final_stage
            funnel.completed_at = current_time
            funnel.is_active = False
            funnel.is_completed = True
            
            # Update conversion data
            if not funnel.funnel_data:
                funnel.funnel_data = {}
            
            funnel.funnel_data.update({
                "time_to_convert": time_to_convert,
                "conversion_value": conversion_data.get("conversion_value"),
                "final_stage": final_stage
            })
            
            self.db.commit()
            
            # Emit event
            self.event_bus.publish(
                "conversion_funnel_completed",
                {
                    "funnel_id": funnel_id,
                    "user_id": funnel.user_id,
                    "funnel_type": funnel.funnel_type,
                    "final_stage": final_stage,
                    "time_to_convert": time_to_convert,
                    "conversion_value": conversion_data.get("conversion_value")
                }
            )
            
            logger.info(f"Completed conversion funnel {funnel_id} with stage {final_stage}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to complete conversion funnel {funnel_id}: {e}")
            return False
    
    def track_offer_interaction(self, user_id: int, offer_type: str, interaction_type: str, metadata: Dict) -> bool:
        """
        Track user interaction with offers
        
        Args:
            user_id: User ID
            offer_type: Type of offer ('trial', 'discount', 'upsell', 'cross_sell')
            interaction_type: Type of interaction ('shown', 'clicked', 'converted', 'dismissed')
            metadata: Additional metadata about the interaction
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from database.models import ConversionFunnel
            
            # Get active conversion funnels for user
            active_funnels = self.db.query(ConversionFunnel).filter(
                ConversionFunnel.user_id == user_id,
                ConversionFunnel.is_active == True
            ).all()
            
            for funnel in active_funnels:
                if not funnel.funnel_data:
                    funnel.funnel_data = {}
                
                # Track offers shown
                if interaction_type == "shown":
                    funnel.funnel_data["offers_shown"] = funnel.funnel_data.get("offers_shown", 0) + 1
                
                # Track offers clicked
                elif interaction_type == "clicked":
                    funnel.funnel_data["offers_clicked"] = funnel.funnel_data.get("offers_clicked", 0) + 1
                
                # Track barriers
                elif interaction_type == "dismissed":
                    barrier = metadata.get("barrier", "unknown")
                    if "barriers_encountered" not in funnel.funnel_data:
                        funnel.funnel_data["barriers_encountered"] = []
                    
                    if barrier not in funnel.funnel_data["barriers_encountered"]:
                        funnel.funnel_data["barriers_encountered"].append(barrier)
            
            self.db.commit()
            
            # Emit event
            self.event_bus.publish(
                "offer_interaction_tracked",
                {
                    "user_id": user_id,
                    "offer_type": offer_type,
                    "interaction_type": interaction_type,
                    "metadata": metadata
                }
            )
            
            logger.info(f"Tracked {interaction_type} interaction for {offer_type} offer for user {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to track offer interaction for user {user_id}: {e}")
            return False
    
    def get_contextual_offers(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get contextual offers based on user's conversion stage and archetype
        
        Args:
            user_id: User ID
            
        Returns:
            List of contextual offers
        """
        try:
            from database.models import ConversionFunnel
            
            # Get user archetype
            archetype_data = self.archetype_engine.detect_archetype(user_id)
            archetype = archetype_data.get('primary_archetype', 'explorer')
            
            # Get active conversion funnels
            active_funnels = self.db.query(ConversionFunnel).filter(
                ConversionFunnel.user_id == user_id,
                ConversionFunnel.is_active == True
            ).all()
            
            offers = []
            
            for funnel in active_funnels:
                stage_offers = self._get_offers_for_stage(funnel.stage_current, archetype)
                offers.extend(stage_offers)
            
            # Limit to 3 most relevant offers
            offers = offers[:3]
            
            # Track offers shown
            for offer in offers:
                self.track_offer_interaction(
                    user_id=user_id,
                    offer_type=offer.get("type", "unknown"),
                    interaction_type="shown",
                    metadata={"offer_id": offer.get("id")}
                )
            
            return offers
            
        except Exception as e:
            logger.error(f"Failed to get contextual offers for user {user_id}: {e}")
            return []
    
    def _get_offers_for_stage(self, stage: str, archetype: str) -> List[Dict[str, Any]]:
        """
        Get offers for specific conversion stage and archetype
        
        Args:
            stage: Conversion stage
            archetype: User archetype
            
        Returns:
            List of offers
        """
        # Base offers by stage
        stage_offers = {
            SubscriptionStage.FREE_TRIAL.value: [
                {
                    "id": "free_trial_7d",
                    "type": "trial",
                    "title": "7-Day Free Trial",
                    "description": "Experience VIP features for 7 days",
                    "value": "free",
                    "duration_days": 7,
                    "priority": 1
                }
            ],
            SubscriptionStage.ENGAGEMENT.value: [
                {
                    "id": "engagement_discount_20",
                    "type": "discount",
                    "title": "20% Engagement Discount",
                    "description": "Special discount for active users",
                    "value": "20% off",
                    "priority": 2
                }
            ],
            SubscriptionStage.CONSIDERATION.value: [
                {
                    "id": "monthly_subscription",
                    "type": "subscription",
                    "title": "Monthly VIP Access",
                    "description": "Full VIP features for one month",
                    "value": "$9.99/month",
                    "duration_days": 30,
                    "priority": 1
                }
            ],
            SubscriptionStage.CONVERSION.value: [
                {
                    "id": "yearly_subscription",
                    "type": "subscription",
                    "title": "Yearly VIP (Best Value)",
                    "description": "Save 40% with yearly subscription",
                    "value": "$59.99/year",
                    "duration_days": 365,
                    "priority": 1
                }
            ],
            SubscriptionStage.ACTIVE_VIP.value: [
                {
                    "id": "referral_bonus",
                    "type": "upsell",
                    "title": "Refer a Friend",
                    "description": "Get 1 month free for each friend who subscribes",
                    "value": "free_month",
                    "priority": 3
                }
            ],
            SubscriptionStage.RENEWAL.value: [
                {
                    "id": "renewal_discount_15",
                    "type": "discount",
                    "title": "Renewal Special",
                    "description": "15% off for loyal customers",
                    "value": "15% off",
                    "priority": 1
                }
            ],
            SubscriptionStage.CHURN_RISK.value: [
                {
                    "id": "winback_offer",
                    "type": "winback",
                    "title": "We Miss You!",
                    "description": "Special offer to keep your VIP benefits",
                    "value": "25% off next month",
                    "priority": 1
                }
            ]
        }
        
        # Archetype-specific adjustments
        archetype_modifiers = {
            "explorer": {"description_suffix": " - Perfect for discovering new content"},
            "collector": {"description_suffix": " - Build your exclusive collection"},
            "socializer": {"description_suffix": " - Share with your community"},
            "achiever": {"description_suffix": " - Unlock advanced achievements"}
        }
        
        offers = stage_offers.get(stage, [])
        
        # Apply archetype customization
        if archetype in archetype_modifiers:
            for offer in offers:
                offer["description"] += archetype_modifiers[archetype]["description_suffix"]
        
        return offers
    
    def handle_subscription_conversion(self, user_id: int, subscription_type: str, payment_data: Dict) -> bool:
        """
        Handle subscription conversion and complete relevant funnels
        
        Args:
            user_id: User ID
            subscription_type: Type of subscription
            payment_data: Payment information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from database.models import ConversionFunnel
            
            # Get active conversion funnels
            active_funnels = self.db.query(ConversionFunnel).filter(
                ConversionFunnel.user_id == user_id,
                ConversionFunnel.is_active == True
            ).all()
            
            conversion_value = payment_data.get("amount", 0)
            
            for funnel in active_funnels:
                # Complete the funnel
                self.complete_conversion_funnel(
                    funnel_id=funnel.id,
                    final_stage=SubscriptionStage.CONVERSION.value,
                    conversion_data={
                        "conversion_value": conversion_value,
                        "subscription_type": subscription_type,
                        "payment_method": payment_data.get("payment_method")
                    }
                )
            
            # Emit conversion event
            self.event_bus.publish(
                "subscription_converted",
                {
                    "user_id": user_id,
                    "subscription_type": subscription_type,
                    "conversion_value": conversion_value,
                    "payment_data": payment_data
                }
            )
            
            logger.info(f"Handled subscription conversion for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle subscription conversion for user {user_id}: {e}")
            return False


# Convenience functions
def start_conversion_funnel(db: Session, user_id: int, funnel_type: str, initial_stage: str) -> bool:
    """Start tracking a user's conversion journey"""
    service = SubscriptionLifecycle(db)
    return service.start_conversion_funnel(user_id, funnel_type, initial_stage)

def update_conversion_stage(db: Session, funnel_id: int, new_stage: str, metadata: Optional[Dict] = None) -> bool:
    """Update user's current stage in conversion funnel"""
    service = SubscriptionLifecycle(db)
    return service.update_conversion_stage(funnel_id, new_stage, metadata)

def complete_conversion_funnel(db: Session, funnel_id: int, final_stage: str, conversion_data: Dict) -> bool:
    """Mark conversion funnel as completed"""
    service = SubscriptionLifecycle(db)
    return service.complete_conversion_funnel(funnel_id, final_stage, conversion_data)

def track_offer_interaction(db: Session, user_id: int, offer_type: str, interaction_type: str, metadata: Dict) -> bool:
    """Track user interaction with offers"""
    service = SubscriptionLifecycle(db)
    return service.track_offer_interaction(user_id, offer_type, interaction_type, metadata)

def get_contextual_offers(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Get contextual offers based on user's conversion stage and archetype"""
    service = SubscriptionLifecycle(db)
    return service.get_contextual_offers(user_id)

def handle_subscription_conversion(db: Session, user_id: int, subscription_type: str, payment_data: Dict) -> bool:
    """Handle subscription conversion and complete relevant funnels"""
    service = SubscriptionLifecycle(db)
    return service.handle_subscription_conversion(user_id, subscription_type, payment_data)