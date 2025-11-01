"""
Event Collector for DianaBot Analytics System
Handles collection, buffering, and storage of analytics events
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsEvent:
    """Base analytics event structure"""
    event_type: str
    user_id: int
    timestamp: datetime
    metadata: Dict[str, Any]
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for storage"""
        return {
            'event_type': self.event_type,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'session_id': self.session_id
        }


class EventCollectorBuffer:
    """Buffer for analytics events to optimize database writes"""
    
    def __init__(self, max_size: int = 100, flush_interval: int = 30):
        self.max_size = max_size
        self.flush_interval = flush_interval
        self.buffer: List[AnalyticsEvent] = []
        self._flush_task: Optional[asyncio.Task] = None
        self._running = False
        self._flush_handler: Optional[Any] = None
        
    async def start(self):
        """Start the automatic flush task"""
        if self._running:
            return
            
        self._running = True
        self._flush_task = asyncio.create_task(self._auto_flush())
        logger.info("EventCollectorBuffer started")
    
    async def stop(self):
        """Stop the buffer and flush remaining events"""
        if not self._running:
            return
            
        self._running = False
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # Flush remaining events
        if self.buffer:
            await self._flush()
        logger.info("EventCollectorBuffer stopped")
    
    async def add_event(self, event: AnalyticsEvent):
        """Add event to buffer, flush if buffer is full"""
        self.buffer.append(event)
        
        if len(self.buffer) >= self.max_size:
            await self._flush()
    
    async def _auto_flush(self):
        """Automatically flush buffer at regular intervals"""
        while self._running:
            await asyncio.sleep(self.flush_interval)
            if self.buffer:
                await self._flush()
    
    async def _flush(self):
        """Flush buffer to storage using the flush handler"""
        if not self.buffer:
            return
            
        events_to_flush = self.buffer.copy()
        self.buffer.clear()
        
        logger.info(f"Flushing {len(events_to_flush)} analytics events")
        
        # Use flush handler if available
        if self._flush_handler:
            await self._flush_handler(events_to_flush)
        
        return events_to_flush


class EventCollector:
    """Main event collector for DianaBot analytics"""
    
    def __init__(self, db_connection, buffer_size: int = 100, flush_interval: int = 30):
        self.db = db_connection
        self.buffer = EventCollectorBuffer(buffer_size, flush_interval)
        self._buffer_flush_handler = None
        
    async def start(self):
        """Start the event collector and buffer"""
        # Set the flush handler for the buffer
        self.buffer._flush_handler = self._store_events
        await self.buffer.start()
        logger.info("EventCollector started")
    
    async def stop(self):
        """Stop the event collector"""
        await self.buffer.stop()
        logger.info("EventCollector stopped")
    
    async def record_event(self, event_type: str, user_id: int, 
                          metadata: Optional[Dict[str, Any]] = None,
                          session_id: Optional[str] = None):
        """Record an analytics event"""
        event = AnalyticsEvent(
            event_type=event_type,
            user_id=user_id,
            timestamp=datetime.now(),
            metadata=metadata or {},
            session_id=session_id
        )
        
        await self.buffer.add_event(event)
        logger.debug(f"Recorded analytics event: {event_type} for user {user_id}")
    
    async def _store_events(self, events: List[AnalyticsEvent]):
        """Store events in database"""
        if not events:
            return
            
        try:
            await self._store_events_in_db(events)
            logger.info(f"Stored {len(events)} analytics events")
            
        except Exception as e:
            logger.error(f"Error storing analytics events: {e}")
            # In production, you might want to implement retry logic here
    
    async def _store_events_in_db(self, events: List[AnalyticsEvent]):
        """Store events in database using SQLAlchemy models"""
        from sqlalchemy import insert
        from database.models import AnalyticsEvent as AnalyticsEventModel
        
        # Convert our AnalyticsEvent objects to database model format
        event_data = []
        for event in events:
            event_data.append({
                'event_type': event.event_type,
                'user_id': event.user_id,
                'session_id': event.session_id,
                'timestamp': event.timestamp,
                'metadata': event.metadata
            })
        
        # Batch insert events
        if event_data:
            stmt = insert(AnalyticsEventModel).values(event_data)
            await self.db.execute(stmt)


# Common event types for DianaBot
EVENT_TYPES = {
    'USER_LOGIN': 'user_login',
    'USER_LOGOUT': 'user_logout',
    'MESSAGE_SENT': 'message_sent',
    'REACTION_ADDED': 'reaction_added',
    'MISSION_COMPLETED': 'mission_completed',
    'ACHIEVEMENT_UNLOCKED': 'achievement_unlocked',
    'BESITOS_EARNED': 'besitos_earned',
    'CONTENT_VIEWED': 'content_viewed',
    'TRIVIA_ANSWERED': 'trivia_answered',
    'AUCTION_PARTICIPATION': 'auction_participation'
}