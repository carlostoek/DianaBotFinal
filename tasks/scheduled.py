#!/usr/bin/env python3
"""
Scheduled tasks for DianaBot
- Subscription expiration checks
- VIP membership verification
- Automated notifications
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_db
from database.models import Subscription
from modules.admin.subscriptions import SubscriptionService
from modules.admin.vip_access import VIPAccessControl

logger = logging.getLogger(__name__)


class ScheduledTasks:
    """Scheduled tasks for automated subscription management"""
    
    def __init__(self):
        self.vip_access = VIPAccessControl()
    
    def check_expiring_subscriptions(self) -> List[dict]:
        """
        Check for subscriptions expiring in the next 3 days
        Returns list of users with expiring subscriptions
        """
        
        try:
            subscription_service = SubscriptionService()
            expiring_subscriptions = subscription_service.get_expiring_subscriptions(days_before=3)
            
            notifications = []
            for subscription in expiring_subscriptions:
                days_until_expiry = (subscription.end_date - datetime.now()).days
                
                notifications.append({
                    'user_id': subscription.user_id,
                    'subscription_type': subscription.subscription_type,
                    'end_date': subscription.end_date,
                    'days_until_expiry': days_until_expiry,
                    'auto_renew': subscription.auto_renew
                })
            
            logger.info(f"Found {len(notifications)} subscriptions expiring soon")
            return notifications
            
        except Exception as e:
            logger.error(f"Error checking expiring subscriptions: {e}")
            return []
    
    def process_expired_subscriptions(self) -> List[dict]:
        """
        Process subscriptions that have expired
        Returns list of users whose subscriptions expired
        """
        
        try:
            subscription_service = SubscriptionService()
            expired_subscriptions = subscription_service.get_expiring_subscriptions(days_before=0)
            
            processed = []
            for subscription in expired_subscriptions:
                # Cancel the subscription
                subscription_service.cancel_subscription(subscription.id)
                
                processed.append({
                    'user_id': subscription.user_id,
                    'subscription_type': subscription.subscription_type,
                    'end_date': subscription.end_date
                })
            
            logger.info(f"Processed {len(processed)} expired subscriptions")
            return processed
            
        except Exception as e:
            logger.error(f"Error processing expired subscriptions: {e}")
            return []
    
    def send_expiration_reminders(self) -> List[dict]:
        """
        Send reminders for expiring subscriptions
        Returns list of reminders sent
        """
        expiring_subscriptions = self.check_expiring_subscriptions()
        
        reminders_sent = []
        for subscription in expiring_subscriptions:
            # In a real implementation, this would send actual Telegram messages
            # For now, we'll just log the reminder
            
            reminder_message = (
                f"Reminder: Your {subscription['subscription_type']} subscription "
                f"expires in {subscription['days_until_expiry']} days "
                f"({subscription['end_date'].strftime('%d/%m/%Y')})"
            )
            
            if subscription['auto_renew']:
                reminder_message += "\n🔄 Auto-renewal is enabled"
            else:
                reminder_message += "\n⚠️ Auto-renewal is disabled - renew manually"
            
            logger.info(f"Reminder for user {subscription['user_id']}: {reminder_message}")
            
            reminders_sent.append({
                'user_id': subscription['user_id'],
                'message': reminder_message,
                'days_until_expiry': subscription['days_until_expiry']
            })
        
        return reminders_sent


def run_scheduled_tasks():
    """Run all scheduled tasks"""
    tasks = ScheduledTasks()
    
    logger.info("Starting scheduled tasks...")
    
    # Check for expiring subscriptions
    expiring = tasks.check_expiring_subscriptions()
    
    # Process expired subscriptions
    expired = tasks.process_expired_subscriptions()
    
    # Send expiration reminders
    reminders = tasks.send_expiration_reminders()
    
    logger.info(f"Scheduled tasks completed: {len(expiring)} expiring, {len(expired)} expired, {len(reminders)} reminders")
    
    return {
        'expiring_subscriptions': expiring,
        'expired_subscriptions': expired,
        'reminders_sent': reminders
    }


if __name__ == "__main__":
    # Run tasks when executed directly
    results = run_scheduled_tasks()
    print(f"Scheduled tasks completed: {results}")