"""
Event Subscriber for DianaBot Analytics System
Automatically subscribes to Event Bus and forwards events to collector
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class AnalyticsEventSubscriber:
    """Subscribes to Event Bus and forwards relevant events to analytics collector"""
    
    def __init__(self, event_collector, event_bus):
        self.collector = event_collector
        self.event_bus = event_bus
        self._subscriptions = {}
    
    async def start(self):
        """Start the subscriber and register event handlers"""
        await self._subscribe_to_events()
        logger.info("AnalyticsEventSubscriber started")
    
    async def stop(self):
        """Stop the subscriber and unsubscribe from events"""
        for event_type, subscription_id in self._subscriptions.items():
            await self.event_bus.unsubscribe(event_type, subscription_id)
        self._subscriptions.clear()
        logger.info("AnalyticsEventSubscriber stopped")
    
    async def _subscribe_to_events(self):
        """Subscribe to relevant events from the Event Bus"""
        # User interaction events
        self._subscriptions['user_login'] = await self.event_bus.subscribe(
            'user_login', self._handle_user_login
        )
        
        self._subscriptions['user_logout'] = await self.event_bus.subscribe(
            'user_logout', self._handle_user_logout
        )
        
        # Gamification events
        self._subscriptions['reaction_added'] = await self.event_bus.subscribe(
            'reaction_added', self._handle_reaction_added
        )
        
        self._subscriptions['mission_completed'] = await self.event_bus.subscribe(
            'mission_completed', self._handle_mission_completed
        )
        
        self._subscriptions['achievement_unlocked'] = await self.event_bus.subscribe(
            'achievement_unlocked', self._handle_achievement_unlocked
        )
        
        self._subscriptions['besitos_earned'] = await self.event_bus.subscribe(
            'besitos_earned', self._handle_besitos_earned
        )
        
        # Content events
        self._subscriptions['content_viewed'] = await self.event_bus.subscribe(
            'content_viewed', self._handle_content_viewed
        )
        
        self._subscriptions['trivia_answered'] = await self.event_bus.subscribe(
            'trivia_answered', self._handle_trivia_answered
        )
        
        self._subscriptions['auction_participation'] = await self.event_bus.subscribe(
            'auction_participation', self._handle_auction_participation
        )
        
        logger.info(f"Subscribed to {len(self._subscriptions)} event types")
    
    async def _handle_user_login(self, data: Dict[str, Any]):
        """Handle user login event"""
        try:
            await self.collector.record_event(
                event_type='user_login',
                user_id=data.get('user_id'),
                metadata={
                    'session_id': data.get('session_id'),
                    'platform': data.get('platform', 'telegram')
                },
                session_id=data.get('session_id')
            )
        except Exception as e:
            logger.error(f"Error handling user_login event: {e}")
    
    async def _handle_user_logout(self, data: Dict[str, Any]):
        """Handle user logout event"""
        try:
            await self.collector.record_event(
                event_type='user_logout',
                user_id=data.get('user_id'),
                metadata={
                    'session_id': data.get('session_id'),
                    'session_duration': data.get('session_duration')
                },
                session_id=data.get('session_id')
            )
        except Exception as e:
            logger.error(f"Error handling user_logout event: {e}")
    
    async def _handle_reaction_added(self, data: Dict[str, Any]):
        """Handle reaction added event"""
        try:
            await self.collector.record_event(
                event_type='reaction_added',
                user_id=data.get('user_id'),
                metadata={
                    'reaction_type': data.get('reaction_type'),
                    'content_id': data.get('content_id'),
                    'besitos_earned': data.get('besitos_earned', 0)
                }
            )
        except Exception as e:
            logger.error(f"Error handling reaction_added event: {e}")
    
    async def _handle_mission_completed(self, data: Dict[str, Any]):
        """Handle mission completed event"""
        try:
            await self.collector.record_event(
                event_type='mission_completed',
                user_id=data.get('user_id'),
                metadata={
                    'mission_id': data.get('mission_id'),
                    'mission_type': data.get('mission_type'),
                    'reward_besitos': data.get('reward_besitos', 0)
                }
            )
        except Exception as e:
            logger.error(f"Error handling mission_completed event: {e}")
    
    async def _handle_achievement_unlocked(self, data: Dict[str, Any]):
        """Handle achievement unlocked event"""
        try:
            await self.collector.record_event(
                event_type='achievement_unlocked',
                user_id=data.get('user_id'),
                metadata={
                    'achievement_id': data.get('achievement_id'),
                    'achievement_name': data.get('achievement_name'),
                    'tier': data.get('tier')
                }
            )
        except Exception as e:
            logger.error(f"Error handling achievement_unlocked event: {e}")
    
    async def _handle_besitos_earned(self, data: Dict[str, Any]):
        """Handle besitos earned event"""
        try:
            await self.collector.record_event(
                event_type='besitos_earned',
                user_id=data.get('user_id'),
                metadata={
                    'amount': data.get('amount', 0),
                    'source': data.get('source'),
                    'transaction_id': data.get('transaction_id')
                }
            )
        except Exception as e:
            logger.error(f"Error handling besitos_earned event: {e}")
    
    async def _handle_content_viewed(self, data: Dict[str, Any]):
        """Handle content viewed event"""
        try:
            await self.collector.record_event(
                event_type='content_viewed',
                user_id=data.get('user_id'),
                metadata={
                    'content_type': data.get('content_type'),
                    'content_id': data.get('content_id'),
                    'channel_id': data.get('channel_id')
                }
            )
        except Exception as e:
            logger.error(f"Error handling content_viewed event: {e}")
    
    async def _handle_trivia_answered(self, data: Dict[str, Any]):
        """Handle trivia answered event"""
        try:
            await self.collector.record_event(
                event_type='trivia_answered',
                user_id=data.get('user_id'),
                metadata={
                    'trivia_id': data.get('trivia_id'),
                    'correct': data.get('correct', False),
                    'reward_besitos': data.get('reward_besitos', 0)
                }
            )
        except Exception as e:
            logger.error(f"Error handling trivia_answered event: {e}")
    
    async def _handle_auction_participation(self, data: Dict[str, Any]):
        """Handle auction participation event"""
        try:
            await self.collector.record_event(
                event_type='auction_participation',
                user_id=data.get('user_id'),
                metadata={
                    'auction_id': data.get('auction_id'),
                    'action': data.get('action'),  # bid, win, lose
                    'bid_amount': data.get('bid_amount', 0)
                }
            )
        except Exception as e:
            logger.error(f"Error handling auction_participation event: {e}")