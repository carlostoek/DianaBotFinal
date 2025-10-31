"""
Channels management module for Telegram channels
Handles free and VIP channels configuration and membership verification
"""

import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import Channel, ChannelPost
from database.connection import get_db

logger = logging.getLogger(__name__)


class ChannelService:
    """Service for managing Telegram channels"""
    
    def __init__(self):
        self.db = next(get_db())
    
    def configure_channel(self, channel_id: int, channel_type: str, channel_title: str, 
                         channel_username: Optional[str] = None, settings: Optional[Dict] = None) -> Channel:
        """
        Configure a new channel or update existing channel configuration
        
        Args:
            channel_id: Telegram channel ID
            channel_type: Type of channel ('free', 'vip', 'announcements')
            channel_title: Channel title
            channel_username: Channel username (optional)
            settings: Channel settings (welcome_message, rules, etc.)
            
        Returns:
            Channel: The configured channel
        """
        try:
            # Check if channel already exists
            existing_channel = self.db.query(Channel).filter(Channel.channel_id == channel_id).first()
            
            if existing_channel:
                # Update existing channel by creating a new instance
                self.db.delete(existing_channel)
                self.db.commit()
                
                # Create updated channel
                channel = Channel(
                    channel_id=channel_id,
                    channel_type=channel_type,
                    channel_title=channel_title,
                    channel_username=channel_username,
                    settings=settings or {}
                )
                
                self.db.add(channel)
                self.db.commit()
                self.db.refresh(channel)
                
                logger.info(f"Updated channel configuration: {channel_id} ({channel_type})")
                return channel
            else:
                # Create new channel
                channel = Channel(
                    channel_id=channel_id,
                    channel_type=channel_type,
                    channel_title=channel_title,
                    channel_username=channel_username,
                    settings=settings or {}
                )
                
                self.db.add(channel)
                self.db.commit()
                self.db.refresh(channel)
                
                logger.info(f"Created new channel: {channel_id} ({channel_type})")
                return channel
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error configuring channel {channel_id}: {e}")
            raise
    
    def get_channel_config(self, channel_id: int) -> Optional[Channel]:
        """
        Get channel configuration
        
        Args:
            channel_id: Telegram channel ID
            
        Returns:
            Optional[Channel]: Channel configuration or None if not found
        """
        try:
            return self.db.query(Channel).filter(Channel.channel_id == channel_id).first()
        except Exception as e:
            logger.error(f"Error getting channel config {channel_id}: {e}")
            return None
    
    def get_channels_by_type(self, channel_type: str) -> list[Channel]:
        """
        Get all channels of a specific type
        
        Args:
            channel_type: Type of channel ('free', 'vip', 'announcements')
            
        Returns:
            list[Channel]: List of channels
        """
        try:
            return self.db.query(Channel).filter(
                Channel.channel_type == channel_type,
                Channel.is_active == True
            ).all()
        except Exception as e:
            logger.error(f"Error getting channels by type {channel_type}: {e}")
            return []
    
    def verify_channel_membership(self, user_id: int, channel_type: str) -> bool:
        """
        Verify if a user is member of a specific channel type
        
        Note: This requires the bot to have admin permissions in the channel
        and the channel to be configured in the database
        
        Args:
            user_id: Telegram user ID
            channel_type: Type of channel to verify ('free', 'vip')
            
        Returns:
            bool: True if user is member, False otherwise
        """
        try:
            channels = self.get_channels_by_type(channel_type)
            
            if not channels:
                logger.warning(f"No {channel_type} channels configured")
                return False
            
            # For now, return True if channels exist
            # In production, this would use Telegram Bot API to check membership
            logger.info(f"Channel membership check for user {user_id} in {channel_type} channels")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying channel membership for user {user_id}: {e}")
            return False
    
    def generate_invite_link(self, channel_type: str, user_id: int) -> Optional[str]:
        """
        Generate an invite link for a specific channel type
        
        Args:
            channel_type: Type of channel ('free', 'vip')
            user_id: User ID for tracking
            
        Returns:
            Optional[str]: Invite link or None if not available
        """
        try:
            channels = self.get_channels_by_type(channel_type)
            
            if not channels:
                logger.warning(f"No {channel_type} channels available for invite")
                return None
            
            # Use the first channel of the type
            channel = channels[0]
            
            # Generate a unique invite link
            # In production, this would use Telegram Bot API to create invite links
            if channel.channel_username is not None and str(channel.channel_username) != "":
                invite_link = f"https://t.me/{channel.channel_username}"
            else:
                # For private channels without username
                invite_link = f"https://t.me/c/{str(channel.channel_id)[4:]}"
            
            logger.info(f"Generated invite link for user {user_id} to {channel_type} channel")
            return invite_link
            
        except Exception as e:
            logger.error(f"Error generating invite link for user {user_id}: {e}")
            return None
    
    def log_channel_post(self, channel_id: int, post_id: int, post_type: str, 
                        content: Optional[str] = None, post_metadata: Optional[Dict] = None) -> ChannelPost:
        """
        Log a channel post for tracking
        
        Args:
            channel_id: Telegram channel ID
            post_id: Telegram post ID
            post_type: Type of post ('welcome', 'announcement', 'content', 'reminder')
            content: Post content (optional)
            metadata: Post metadata (optional)
            
        Returns:
            ChannelPost: The logged post
        """
        try:
            post = ChannelPost(
                channel_id=channel_id,
                post_id=post_id,
                post_type=post_type,
                content=content,
                post_metadata=post_metadata or {}
            )
            
            self.db.add(post)
            self.db.commit()
            self.db.refresh(post)
            
            logger.info(f"Logged channel post: {post_id} in channel {channel_id}")
            return post
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error logging channel post {post_id}: {e}")
            raise
    
    def get_channel_stats(self, channel_id: int) -> Dict[str, Any]:
        """
        Get channel statistics
        
        Args:
            channel_id: Telegram channel ID
            
        Returns:
            Dict[str, Any]: Channel statistics
        """
        try:
            channel = self.get_channel_config(channel_id)
            if not channel:
                return {}
            
            # Get post counts by type
            post_counts = self.db.query(
                ChannelPost.post_type,
                func.count(ChannelPost.id)
            ).filter(
                ChannelPost.channel_id == channel_id
            ).group_by(ChannelPost.post_type).all()
            
            stats = {
                "channel_id": channel_id,
                "channel_type": channel.channel_type,
                "channel_title": channel.channel_title,
                "is_active": channel.is_active,
                "post_counts": {post_type: count for post_type, count in post_counts},
                "total_posts": sum(count for _, count in post_counts)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting channel stats for {channel_id}: {e}")
            return {}


# Global instance
channel_service = ChannelService()