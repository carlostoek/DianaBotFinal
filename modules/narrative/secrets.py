"""
Secret system for hidden narrative fragments and discovery mechanics
"""
import hashlib
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from database.models import (
    NarrativeFragment, UserNarrativeProgress, User, 
    UserInventory, UserSecretDiscovery, SecretCode
)
from database.connection import get_db
from core.event_bus import EventBus


class SecretService:
    """Service for managing secret fragments and discovery mechanics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.event_bus = EventBus()
    
    def submit_secret_code(self, user_id: int, code: str) -> Optional[Dict[str, Any]]:
        """
        Submit a secret code and unlock corresponding fragment if valid
        
        Args:
            user_id: User ID
            code: Secret code to verify
            
        Returns:
            Dictionary with result info or None if invalid
        """
        # Normalize code
        normalized_code = code.strip().upper()
        
        # Find secret code
        secret_code = self.db.query(SecretCode).filter(
            SecretCode.code == normalized_code,
            SecretCode.is_active == True
        ).first()
        
        if not secret_code:
            return None
        
        # Check if user already discovered this
        existing_discovery = self.db.query(UserSecretDiscovery).filter(
            UserSecretDiscovery.user_id == user_id,
            UserSecretDiscovery.secret_code_id == secret_code.id
        ).first()
        
        if existing_discovery:
            return {
                "success": False,
                "message": "Ya has descubierto este secreto",
                "fragment_key": secret_code.fragment_key
            }
        
        # Find the secret fragment
        fragment = self.db.query(NarrativeFragment).filter(
            NarrativeFragment.fragment_key == secret_code.fragment_key,
            NarrativeFragment.is_secret == True,
            NarrativeFragment.is_active == True
        ).first()
        
        if not fragment:
            return None
        
        # Record discovery
        discovery = UserSecretDiscovery(
            user_id=user_id,
            secret_code_id=secret_code.id,
            fragment_key=secret_code.fragment_key
        )
        self.db.add(discovery)
        
        # Unlock the fragment
        progress = UserNarrativeProgress(
            user_id=user_id,
            fragment_id=fragment.id
        )
        self.db.add(progress)
        
        self.db.commit()
        
        # Publish secret discovered event
        self.event_bus.publish("narrative.secret_discovered", {
            "user_id": user_id,
            "fragment_key": secret_code.fragment_key,
            "fragment_title": fragment.title,
            "code": normalized_code
        })
        
        return {
            "success": True,
            "message": f"¡Secreto descubierto! Has desbloqueado: {fragment.title}",
            "fragment_key": secret_code.fragment_key,
            "fragment_title": fragment.title
        }
    
    def verify_secret_code(self, code: str) -> bool:
        """Verify if a secret code is valid"""
        normalized_code = code.strip().upper()
        
        secret_code = self.db.query(SecretCode).filter(
            SecretCode.code == normalized_code,
            SecretCode.is_active == True
        ).first()
        
        return secret_code is not None
    
    def unlock_secret_fragment(self, user_id: int, fragment_key: str) -> bool:
        """
        Unlock a secret fragment for a user
        
        Args:
            user_id: User ID
            fragment_key: Fragment key to unlock
            
        Returns:
            True if unlocked successfully
        """
        fragment = self.db.query(NarrativeFragment).filter(
            NarrativeFragment.fragment_key == fragment_key,
            NarrativeFragment.is_secret == True,
            NarrativeFragment.is_active == True
        ).first()
        
        if not fragment:
            return False
        
        # Check if already unlocked
        existing_progress = self.db.query(UserNarrativeProgress).filter(
            UserNarrativeProgress.user_id == user_id,
            UserNarrativeProgress.fragment_id == fragment.id
        ).first()
        
        if existing_progress:
            return True
        
        # Unlock fragment
        progress = UserNarrativeProgress(
            user_id=user_id,
            fragment_id=fragment.id
        )
        self.db.add(progress)
        self.db.commit()
        
        # Publish event
        self.event_bus.publish("narrative.secret_unlocked", {
            "user_id": user_id,
            "fragment_key": fragment_key,
            "fragment_title": fragment.title
        })
        
        return True
    
    def get_discovered_secrets(self, user_id: int) -> List[Dict[str, Any]]:
        """Get list of secrets discovered by user"""
        discoveries = self.db.query(UserSecretDiscovery).filter(
            UserSecretDiscovery.user_id == user_id
        ).all()
        
        result = []
        for discovery in discoveries:
            fragment = self.db.query(NarrativeFragment).filter(
                NarrativeFragment.fragment_key == discovery.fragment_key
            ).first()
            
            if fragment:
                result.append({
                    "fragment_key": discovery.fragment_key,
                    "fragment_title": fragment.title,
                    "discovered_at": discovery.discovered_at,
                    "code_used": discovery.secret_code.code if discovery.secret_code else None
                })
        
        return result
    
    def check_item_combinations(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Check if user has item combinations that unlock secret fragments
        
        Returns:
            List of unlocked fragments
        """
        # Define item combinations that unlock secrets
        item_combinations = [
            {
                "items": ["ancient_map", "decoder_ring"],
                "fragment_key": "lucien_backstory",
                "description": "Mapa Antiguo + Anillo Decodificador"
            },
            {
                "items": ["crystal_ball", "mystic_powder"],
                "fragment_key": "prophecy_revealed",
                "description": "Bola de Cristal + Polvo Místico"
            },
            {
                "items": ["silver_key", "golden_lock"],
                "fragment_key": "hidden_chamber",
                "description": "Llave Plateada + Candado Dorado"
            }
        ]
        
        unlocked_fragments = []
        
        for combination in item_combinations:
            # Check if user has all required items
            has_all_items = True
            for item_key in combination["items"]:
                item_count = self.db.query(UserInventory).filter(
                    UserInventory.user_id == user_id,
                    UserInventory.item_id == self._get_item_id_by_key(item_key)
                ).count()
                
                if item_count == 0:
                    has_all_items = False
                    break
            
            if has_all_items:
                # Unlock the secret fragment
                if self.unlock_secret_fragment(user_id, combination["fragment_key"]):
                    unlocked_fragments.append({
                        "fragment_key": combination["fragment_key"],
                        "description": combination["description"],
                        "items": combination["items"]
                    })
        
        return unlocked_fragments
    
    def get_secret_hint(self, user_id: int) -> Optional[str]:
        """
        Get a hint about the next secret the user can discover
        
        Returns:
            Hint message or None if no hints available
        """
        # Get undiscovered secret codes
        discovered_codes = self.db.query(UserSecretDiscovery.secret_code_id).filter(
            UserSecretDiscovery.user_id == user_id
        ).all()
        
        discovered_ids = [dc[0] for dc in discovered_codes]
        
        # Find an undiscovered secret
        undiscovered_secret = self.db.query(SecretCode).filter(
            SecretCode.is_active == True,
            SecretCode.id.notin_(discovered_ids) if discovered_ids else True
        ).first()
        
        if not undiscovered_secret:
            return None
        
        # Return hint based on secret type
        hints = {
            "lucien_backstory": "Busca pistas sobre el pasado de Lucien en los canales VIP",
            "prophecy_revealed": "Combina objetos místicos para revelar la profecía",
            "hidden_chamber": "Algunas llaves abren más que puertas...",
            "alternate_ending": "Las decisiones contraintuitivas pueden llevar a caminos inesperados",
            "character_secret": "Observa cuidadosamente las conversaciones con los personajes"
        }
        
        return hints.get(undiscovered_secret.fragment_key, "Explora cuidadosamente el mundo de Diana")
    
    def _get_item_id_by_key(self, item_key: str) -> Optional[int]:
        """Helper to get item ID by key"""
        from database.models import Item
        
        item = self.db.query(Item).filter(Item.item_key == item_key).first()
        return item.id if item else None


def get_secret_service() -> SecretService:
    """Get secret service instance"""
    db = next(get_db())
    return SecretService(db)