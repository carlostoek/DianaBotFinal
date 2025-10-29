"""
DianaBot - Event Bus System
"""
import json
import asyncio
from typing import Dict, List, Callable, Any
from datetime import datetime
from collections import defaultdict
import redis
from .logger import get_logger
from .settings import settings


logger = get_logger(__name__)


class EventBus:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db,
            decode_responses=True
        )
        self.handlers = defaultdict(list)
        self.pubsub = self.redis_client.pubsub()
        self._setup_pubsub()
    
    def _setup_pubsub(self):
        """Set up pubsub listeners for all registered event types"""
        for event_type in self.handlers.keys():
            self.pubsub.subscribe(f'dianabot:events:{event_type}')
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe a handler to an event type"""
        self.handlers[event_type].append(handler)
        
        # Subscribe to Redis channel if not already subscribed
        if event_type not in self.pubsub.channels:
            self.pubsub.subscribe(f'dianabot:events:{event_type}')
        
        logger.info(f"Handler subscribed to event type: {event_type}")
    
    def publish(self, event_type: str, event_data: Dict[str, Any]):
        """Publish an event to the event bus"""
        event = {
            'type': event_type,
            'data': event_data,
            'timestamp': datetime.now().isoformat(),
            'event_id': self._generate_event_id()
        }
        
        # Publish to Redis
        channel_key = f'dianabot:events:{event_type}'
        self.redis_client.publish(channel_key, json.dumps(event))
        
        logger.info(f"Event published: {event_type} with ID {event['event_id']}")
    
    async def listen(self):
        """Listen for events and dispatch them to handlers"""
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    # Extract event type from channel name
                    channel = message['channel']
                    event_type = channel.split(':')[2]  # 'dianabot:events:event_type'
                    
                    # Parse event data
                    event = json.loads(message['data'])
                    
                    # Dispatch to handlers
                    await self._dispatch_event(event_type, event)
                    
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode JSON from message: {message}")
                except Exception as e:
                    logger.error(f"Error processing event from channel {message['channel']}: {e}")
    
    async def _dispatch_event(self, event_type: str, event: Dict[str, Any]):
        """Dispatch an event to all registered handlers"""
        for handler in self.handlers[event_type]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")
    
    def _generate_event_id(self) -> str:
        """Generate a unique event ID"""
        import uuid
        return str(uuid.uuid4())


# Global event bus instance
event_bus = EventBus()


# Decorator for easy event subscription
def subscribe_to(event_type: str):
    """Decorator to subscribe a function to an event type"""
    def decorator(func):
        event_bus.subscribe(event_type, func)
        return func
    return decorator


# Predefined event types
class EventType:
    # Narrative events
    NARRATIVE_FRAGMENT_STARTED = 'narrative.fragment_started'
    NARRATIVE_DECISION_MADE = 'narrative.decision_made'
    NARRATIVE_FRAGMENT_COMPLETED = 'narrative.fragment_completed'
    NARRATIVE_LEVEL_COMPLETED = 'narrative.level_completed'
    NARRATIVE_SECRET_DISCOVERED = 'narrative.secret_discovered'
    NARRATIVE_CONTENT_UNLOCKED = 'narrative.content_unlocked'
    
    # Gamification events
    GAMIFICATION_BESITOS_EARNED = 'gamification.besitos_earned'
    GAMIFICATION_BESITOS_SPENT = 'gamification.besitos_spent'
    GAMIFICATION_ITEM_PURCHASED = 'gamification.item_purchased'
    GAMIFICATION_ITEM_USED = 'gamification.item_used'
    GAMIFICATION_ACHIEVEMENT_UNLOCKED = 'gamification.achievement_unlocked'
    GAMIFICATION_MISSION_ASSIGNED = 'gamification.mission_assigned'
    GAMIFICATION_MISSION_COMPLETED = 'gamification.mission_completed'
    GAMIFICATION_AUCTION_WON = 'gamification.auction_won'
    GAMIFICATION_TRIVIA_ANSWERED = 'gamification.trivia_answered'
    
    # Administrative events
    ADMIN_SUBSCRIPTION_STARTED = 'admin.subscription_started'
    ADMIN_SUBSCRIPTION_EXPIRING = 'admin.subscription_expiring'
    ADMIN_SUBSCRIPTION_EXPIRED = 'admin.subscription_expired'
    ADMIN_USER_JOINED_CHANNEL = 'admin.user_joined_channel'
    ADMIN_USER_LEFT_CHANNEL = 'admin.user_left_channel'
    ADMIN_CONTENT_PUBLISHED = 'admin.content_published'
    ADMIN_ACCESS_REVOKED = 'admin.access_revoked'