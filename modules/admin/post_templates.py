"""
Post templates for different types of channel content
Provides standardized templates for narrative, mission, trivia, and announcement posts
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PostTemplates:
    """Template system for channel posts"""
    
    @staticmethod
    def create_narrative_post(fragment_title: str, content: str, 
                            choices: Optional[list] = None,
                            is_vip: bool = False) -> Dict[str, Any]:
        """
        Create a narrative post template
        
        Args:
            fragment_title: Title of the narrative fragment
            content: Story content
            choices: List of choices for interactive posts
            is_vip: Whether this is VIP content
            
        Returns:
            Dict[str, Any]: Post template
        """
        template = {
            "type": "narrative",
            "title": fragment_title,
            "content": content,
            "is_vip": is_vip,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "has_choices": bool(choices),
                "choice_count": len(choices) if choices else 0
            }
        }
        
        if choices:
            template["choices"] = choices
            template["content"] += "\n\n💡 *¿Qué decides hacer?*"
        
        if is_vip:
            template["content"] = "💎 **CONTENIDO VIP** 💎\n\n" + template["content"]
        
        return template
    
    @staticmethod
    def create_mission_post(mission_title: str, description: str, 
                          rewards: Dict[str, Any],
                          mission_type: str = "daily") -> Dict[str, Any]:
        """
        Create a mission announcement post
        
        Args:
            mission_title: Mission title
            description: Mission description
            rewards: Reward information
            mission_type: Type of mission
            
        Returns:
            Dict[str, Any]: Post template
        """
        # Format rewards
        reward_text = ""
        if rewards.get("besitos"):
            reward_text += f"💰 {rewards['besitos']} besitos\n"
        if rewards.get("items"):
            reward_text += f"🎁 {', '.join(rewards['items'])}\n"
        if rewards.get("achievements"):
            reward_text += f"🏆 {', '.join(rewards['achievements'])}\n"
        
        content = (
            f"🎯 **{mission_title}**\n\n"
            f"{description}\n\n"
            f"**Recompensas:**\n"
            f"{reward_text}\n"
            f"*Tipo: {mission_type.upper()}*"
        )
        
        return {
            "type": "mission",
            "title": mission_title,
            "content": content,
            "mission_type": mission_type,
            "rewards": rewards,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "has_accept_button": True
            }
        }
    
    @staticmethod
    def create_trivia_post(question: str, options: list, 
                         correct_answer: int,
                         time_limit: int = 300) -> Dict[str, Any]:
        """
        Create a trivia post
        
        Args:
            question: Trivia question
            options: List of answer options
            correct_answer: Index of correct answer (0-based)
            time_limit: Time limit in seconds
            
        Returns:
            Dict[str, Any]: Post template
        """
        content = (
            f"🧠 **TRIVIA DEL DÍA** 🧠\n\n"
            f"{question}\n\n"
        )
        
        # Add options
        for i, option in enumerate(options):
            content += f"{i+1}. {option}\n"
        
        content += f"\n⏰ *Tienes {time_limit//60} minutos para responder*"
        
        return {
            "type": "trivia",
            "title": "Trivia del Día",
            "content": content,
            "options": options,
            "correct_answer": correct_answer,
            "time_limit": time_limit,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "option_count": len(options),
                "has_voting": True
            }
        }
    
    @staticmethod
    def create_announcement_post(title: str, message: str, 
                               announcement_type: str = "general",
                               is_important: bool = False) -> Dict[str, Any]:
        """
        Create an announcement post
        
        Args:
            title: Announcement title
            message: Announcement message
            announcement_type: Type of announcement
            is_important: Whether this is an important announcement
            
        Returns:
            Dict[str, Any]: Post template
        """
        if is_important:
            content = f"🚨 **{title.upper()}** 🚨\n\n{message}"
        else:
            content = f"📢 **{title}**\n\n{message}"
        
        return {
            "type": "announcement",
            "title": title,
            "content": content,
            "announcement_type": announcement_type,
            "is_important": is_important,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "has_pin": is_important
            }
        }
    
    @staticmethod
    def create_event_post(event_title: str, description: str, 
                        start_time: datetime,
                        end_time: datetime,
                        event_type: str = "special") -> Dict[str, Any]:
        """
        Create an event announcement post
        
        Args:
            event_title: Event title
            description: Event description
            start_time: Event start time
            end_time: Event end time
            event_type: Type of event
            
        Returns:
            Dict[str, Any]: Post template
        """
        # Format time
        start_str = start_time.strftime("%d/%m/%Y %H:%M")
        end_str = end_time.strftime("%d/%m/%Y %H:%M")
        
        content = (
            f"🎉 **{event_title.upper()}** 🎉\n\n"
            f"{description}\n\n"
            f"📅 **Fecha:** {start_str} - {end_str}\n"
            f"🎯 **Tipo:** {event_type.upper()}\n\n"
            f"¡No te lo pierdas! 🚀"
        )
        
        return {
            "type": "event",
            "title": event_title,
            "content": content,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "has_countdown": True,
                "duration_hours": int((end_time - start_time).total_seconds() / 3600)
            }
        }
    
    @staticmethod
    def format_post_for_telegram(template: Dict[str, Any]) -> str:
        """
        Format a post template for Telegram
        
        Args:
            template: Post template
            
        Returns:
            str: Formatted content for Telegram
        """
        content = template["content"]
        
        # Add footer based on post type
        if template["type"] == "narrative" and template.get("is_vip"):
            content += "\n\n💎 *Contenido exclusivo para suscriptores VIP*"
        elif template["type"] == "mission":
            content += "\n\n✅ *Usa /missions para ver tus misiones activas*"
        elif template["type"] == "trivia":
            content += "\n\n🎯 *Responde con el número de la opción correcta*"
        
        return content
    
    @staticmethod
    def get_recurring_schedule(post_type: str) -> Optional[str]:
        """
        Get default recurrence for post types
        
        Args:
            post_type: Type of post
            
        Returns:
            Optional[str]: Recurrence pattern
        """
        recurring_posts = {
            "mission": "daily",
            "trivia": "daily",
            "narrative": None,  # Usually not recurring
            "announcement": None,  # One-time
            "event": None  # One-time
        }
        
        return recurring_posts.get(post_type)


# Global instance
post_templates = PostTemplates()