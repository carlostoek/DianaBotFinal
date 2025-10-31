"""
Content publishing service for scheduled posts in Telegram channels
Handles creation, scheduling, and automated publishing of content
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import update
from database.models import ChannelPost, Channel
from database.connection import get_db

logger = logging.getLogger(__name__)


class PublishingService:
    """Service for managing scheduled content publishing"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session or next(get_db())
    
    def create_post(self, channel_id: int, post_type: str, content: str, 
                   scheduled_for: Optional[datetime] = None, 
                   recurrence: Optional[str] = None,
                   is_protected: bool = False,
                   linked_mission_id: Optional[int] = None,
                   linked_fragment_id: Optional[int] = None) -> ChannelPost:
        """
        Create a new channel post
        
        Args:
            channel_id: Telegram channel ID
            post_type: Type of post ('narrative', 'mission', 'announcement', 'trivia', 'event')
            content: Post content
            scheduled_for: When to publish (None for immediate)
            recurrence: Recurrence pattern ('daily', 'weekly', 'monthly')
            is_protected: Protect content from forwarding
            linked_mission_id: Linked mission ID
            linked_fragment_id: Linked narrative fragment ID
            
        Returns:
            ChannelPost: The created post
        """
        try:
            # Determine post status
            status = 'scheduled' if scheduled_for else 'draft'
            
            post = ChannelPost(
                channel_id=channel_id,
                post_type=post_type,
                content=content,
                scheduled_for=scheduled_for,
                status=status,
                recurrence=recurrence,
                is_protected=is_protected,
                linked_mission_id=linked_mission_id,
                linked_fragment_id=linked_fragment_id
            )
            
            self.db.add(post)
            self.db.commit()
            self.db.refresh(post)
            
            logger.info(f"Created {post_type} post for channel {channel_id} (status: {status})")
            return post
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating post for channel {channel_id}: {e}")
            raise
    
    def publish_post(self, post_id: int, bot=None) -> bool:
        """
        Publish a scheduled post
        
        Args:
            post_id: Post ID to publish
            bot: Telegram bot instance (optional)
            
        Returns:
            bool: True if published successfully
        """
        try:
            # Get the post object
            post = self.db.query(ChannelPost).filter(ChannelPost.id == post_id).first()
            if not post:
                logger.error(f"Post {post_id} not found")
                return False
            
            # Check status using the actual value
            post_status = post.status
            if post_status == 'published':
                logger.warning(f"Post {post_id} already published")
                return True
            
            if post_status == 'cancelled':
                logger.warning(f"Post {post_id} is cancelled")
                return False
            
            # If bot is provided, actually publish to Telegram
            if bot is not None:
                channel_config = self.db.query(Channel).filter(Channel.channel_id == post.channel_id).first()
                if not channel_config:
                    logger.error(f"Channel {post.channel_id} not configured")
                    return False
                
                # In production, this would use bot.send_message with proper formatting
                # For now, we'll simulate the publication
                logger.info(f"Publishing post {post_id} to channel {post.channel_id}")
                
                # Update the post using SQLAlchemy update
                stmt = update(ChannelPost).where(ChannelPost.id == post_id).values(
                    status='published',
                    published_at=datetime.now()
                )
                self.db.execute(stmt)
                
                # Handle recurrence
                post_recurrence = post.recurrence
                if post_recurrence:
                    self._reschedule_recurring_post(post)
                
                self.db.commit()
                logger.info(f"Successfully published post {post_id}")
                return True
            else:
                # Just mark as published for testing
                stmt = update(ChannelPost).where(ChannelPost.id == post_id).values(
                    status='published',
                    published_at=datetime.now()
                )
                self.db.execute(stmt)
                self.db.commit()
                logger.info(f"Marked post {post_id} as published (no bot instance)")
                return True
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error publishing post {post_id}: {e}")
            return False
    
    def _reschedule_recurring_post(self, post: ChannelPost) -> Optional[ChannelPost]:
        """
        Reschedule a recurring post
        
        Args:
            post: The original post
            
        Returns:
            Optional[ChannelPost]: The new scheduled post
        """
        try:
            post_recurrence = post.recurrence
            if not post_recurrence:
                return None
            
            # Calculate next scheduled time
            base_time = datetime.now()
            
            if post_recurrence == 'daily':
                next_schedule = base_time + timedelta(days=1)
            elif post_recurrence == 'weekly':
                next_schedule = base_time + timedelta(weeks=1)
            elif post_recurrence == 'monthly':
                # Simple monthly calculation
                next_schedule = base_time + timedelta(days=30)
            else:
                logger.warning(f"Unknown recurrence pattern: {post_recurrence}")
                return None
            
            # Create new scheduled post
            new_post = ChannelPost(
                channel_id=post.channel_id,
                post_type=post.post_type,
                content=post.content,
                scheduled_for=next_schedule,
                status='scheduled',
                recurrence=post_recurrence,
                is_protected=post.is_protected,
                linked_mission_id=post.linked_mission_id,
                linked_fragment_id=post.linked_fragment_id
            )
            
            self.db.add(new_post)
            self.db.commit()
            self.db.refresh(new_post)
            
            logger.info(f"Rescheduled recurring post {post.id} as {new_post.id} for {next_schedule}")
            return new_post
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error rescheduling post {post.id}: {e}")
            return None
    
    def get_scheduled_posts(self, due_before: Optional[datetime] = None) -> List[ChannelPost]:
        """
        Get posts scheduled for publication
        
        Args:
            due_before: Get posts scheduled before this time (None for all scheduled)
            
        Returns:
            List[ChannelPost]: List of scheduled posts
        """
        try:
            query = self.db.query(ChannelPost).filter(
                ChannelPost.status == 'scheduled'
            )
            
            if due_before:
                query = query.filter(ChannelPost.scheduled_for <= due_before)
            
            return query.order_by(ChannelPost.scheduled_for).all()
            
        except Exception as e:
            logger.error(f"Error getting scheduled posts: {e}")
            return []
    
    def cancel_post(self, post_id: int) -> bool:
        """
        Cancel a scheduled post
        
        Args:
            post_id: Post ID to cancel
            
        Returns:
            bool: True if cancelled successfully
        """
        try:
            post = self.db.query(ChannelPost).filter(ChannelPost.id == post_id).first()
            if not post:
                logger.error(f"Post {post_id} not found")
                return False
            
            post_status = post.status
            if post_status == 'published':
                logger.warning(f"Cannot cancel already published post {post_id}")
                return False
            
            # Cancel the post using SQLAlchemy update
            stmt = update(ChannelPost).where(ChannelPost.id == post_id).values(
                status='cancelled'
            )
            self.db.execute(stmt)
            self.db.commit()
            
            logger.info(f"Cancelled post {post_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cancelling post {post_id}: {e}")
            return False
    
    def get_post_stats(self, channel_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get publishing statistics
        
        Args:
            channel_id: Specific channel ID (None for all channels)
            
        Returns:
            Dict[str, Any]: Publishing statistics
        """
        try:
            query = self.db.query(ChannelPost)
            
            if channel_id:
                query = query.filter(ChannelPost.channel_id == channel_id)
            
            posts = query.all()
            
            stats = {
                'total_posts': len(posts),
                'by_status': {},
                'by_type': {},
                'scheduled_count': 0,
                'published_count': 0
            }
            
            for post in posts:
                # Count by status
                post_status = post.status
                stats['by_status'][post_status] = stats['by_status'].get(post_status, 0) + 1
                
                # Count by type
                post_type = post.post_type
                stats['by_type'][post_type] = stats['by_type'].get(post_type, 0) + 1
                
                # Specific counts
                if post_status == 'scheduled':
                    stats['scheduled_count'] += 1
                elif post_status == 'published':
                    stats['published_count'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting post stats: {e}")
            return {}
    
    def get_upcoming_posts(self, hours_ahead: int = 24) -> List[ChannelPost]:
        """
        Get posts scheduled for publication in the next hours
        
        Args:
            hours_ahead: Hours to look ahead
            
        Returns:
            List[ChannelPost]: List of upcoming posts
        """
        try:
            now = datetime.now()
            cutoff_time = now + timedelta(hours=hours_ahead)
            
            return self.db.query(ChannelPost).filter(
                ChannelPost.status == 'scheduled',
                ChannelPost.scheduled_for <= cutoff_time,
                ChannelPost.scheduled_for >= now
            ).order_by(ChannelPost.scheduled_for).all()
            
        except Exception as e:
            logger.error(f"Error getting upcoming posts: {e}")
            return []


# Global instance
publishing_service = PublishingService()