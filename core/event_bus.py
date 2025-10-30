import json
import logging
from typing import Any, Callable, Dict, Optional
import redis
from database.connection import get_redis

logger = logging.getLogger(__name__)


class EventBus:
    """Event Bus implementation using Redis Pub/Sub"""
    
    def __init__(self):
        self.redis_client: redis.Redis = get_redis()
        self.pubsub = self.redis_client.pubsub()
        self.handlers: Dict[str, list[Callable]] = {}
    
    def publish(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Publish an event to Redis channel"""
        try:
            event = {
                'type': event_type,
                'data': event_data,
                'timestamp': self._get_current_timestamp()
            }
            
            message = json.dumps(event)
            self.redis_client.publish(event_type, message)
            
            logger.info(f"Event published: {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            raise
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to an event type with a handler function"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
            # Subscribe to Redis channel
            self.pubsub.subscribe(event_type)
        
        self.handlers[event_type].append(handler)
        logger.info(f"Handler subscribed to event: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe a handler from an event type"""
        if event_type in self.handlers:
            if handler in self.handlers[event_type]:
                self.handlers[event_type].remove(handler)
                
                # If no more handlers, unsubscribe from Redis channel
                if not self.handlers[event_type]:
                    self.pubsub.unsubscribe(event_type)
                    del self.handlers[event_type]
                
                logger.info(f"Handler unsubscribed from event: {event_type}")
    
    def listen(self) -> None:
        """Start listening for events and dispatch to handlers"""
        logger.info("Event Bus listener started")
        
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    event = json.loads(message['data'])
                    event_type = event['type']
                    
                    # Dispatch to all registered handlers
                    if event_type in self.handlers:
                        for handler in self.handlers[event_type]:
                            try:
                                handler(event)
                            except Exception as e:
                                logger.error(f"Handler error for event {event_type}: {e}")
                    
                except Exception as e:
                    logger.error(f"Failed to process message: {e}")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


# Global event bus instance
event_bus = EventBus()