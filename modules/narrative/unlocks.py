"""
Unlock System for Narrative Fragments
Handles conditional access to narrative content based on user state
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User, UserNarrativeProgress, UserBalance, NarrativeFragment

logger = logging.getLogger(__name__)


class UnlockEngine:
    """Engine for evaluating unlock conditions for narrative content"""
    
    def __init__(self):
        pass
    
    def evaluate_conditions(self, user_id: int, conditions: Optional[Dict[str, Any]]) -> bool:
        """
        Evaluate unlock conditions for a user
        
        Args:
            user_id: User ID
            conditions: Conditions dictionary
            
        Returns:
            bool: True if conditions are met
        """
        if not conditions:
            return True
        
        # Handle complex conditions with operators
        if "operator" in conditions:
            return self._evaluate_complex_conditions(user_id, conditions)
        
        # Handle simple conditions
        return self._evaluate_simple_conditions(user_id, conditions)
    
    def _evaluate_complex_conditions(self, user_id: int, conditions: Dict[str, Any]) -> bool:
        """Evaluate complex conditions with AND/OR operators"""
        operator = conditions.get("operator", "AND")
        sub_conditions = conditions.get("conditions", [])
        
        if operator == "AND":
            return all(self.evaluate_conditions(user_id, cond) for cond in sub_conditions)
        elif operator == "OR":
            return any(self.evaluate_conditions(user_id, cond) for cond in sub_conditions)
        else:
            logger.warning(f"Unknown operator: {operator}")
            return False
    
    def _evaluate_simple_conditions(self, user_id: int, conditions: Dict[str, Any]) -> bool:
        """Evaluate simple condition types"""
        
        # Check besitos requirement
        if "min_besitos" in conditions:
            if not self._check_besitos_requirement(user_id, conditions["min_besitos"]):
                return False
        
        # Check item requirement
        if "required_items" in conditions:
            if not self._check_items_requirement(user_id, conditions["required_items"]):
                return False
        
        # Check completed fragments requirement
        if "required_fragments" in conditions:
            if not self._check_fragments_requirement(user_id, conditions["required_fragments"]):
                return False
        
        # Check subscription requirement
        if "subscription" in conditions:
            if not self._check_subscription_requirement(user_id, conditions["subscription"]):
                return False
        
        # Check narrative flags
        if "narrative_flags" in conditions:
            if not self._check_narrative_flags(user_id, conditions["narrative_flags"]):
                return False
        
        return True
    
    def _check_besitos_requirement(self, user_id: int, min_besitos: int) -> bool:
        """Check if user has minimum besitos"""
        db: Session = next(get_db())
        
        try:
            balance = db.query(UserBalance).filter(UserBalance.user_id == user_id).first()
            if balance and balance.besitos >= min_besitos:
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to check besitos for user {user_id}: {e}")
            return False
        finally:
            db.close()
    
    def _check_items_requirement(self, user_id: int, required_items: List[str]) -> bool:
        """Check if user has required items"""
        # TODO: Integrate with inventory system
        # For now, assume user has the items
        logger.info(f"Item requirement check for user {user_id}: {required_items}")
        return True
    
    def _check_fragments_requirement(self, user_id: int, required_fragments: List[str]) -> bool:
        """Check if user has completed required fragments"""
        db: Session = next(get_db())
        
        try:
            for fragment_key in required_fragments:
                # Check if user has completed this fragment
                progress = db.query(UserNarrativeProgress).join(
                    UserNarrativeProgress.fragment
                ).filter(
                    UserNarrativeProgress.user_id == user_id,
                    UserNarrativeProgress.fragment.has(fragment_key=fragment_key)
                ).first()
                
                if not progress:
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to check fragment requirements for user {user_id}: {e}")
            return False
        finally:
            db.close()
    
    def _check_subscription_requirement(self, user_id: int, subscription_type: str) -> bool:
        """Check if user has required subscription"""
        # TODO: Integrate with subscription system
        # For now, assume user has the subscription
        logger.info(f"Subscription requirement check for user {user_id}: {subscription_type}")
        return True
    
    def _check_narrative_flags(self, user_id: int, flags_required: List[str]) -> bool:
        """Check if user has required narrative flags"""
        # TODO: Integrate with narrative state system
        # For now, assume user has the flags
        logger.info(f"Narrative flags check for user {user_id}: {flags_required}")
        return True
    
    def get_missing_requirements(self, user_id: int, conditions: Optional[Dict[str, Any]]) -> List[str]:
        """
        Get list of missing requirements for unlock conditions
        
        Args:
            user_id: User ID
            conditions: Conditions dictionary
            
        Returns:
            list: List of missing requirements
        """
        if not conditions:
            return []
        
        missing = []
        
        # Check besitos requirement
        if "min_besitos" in conditions:
            min_besitos = conditions["min_besitos"]
            db: Session = next(get_db())
            try:
                balance = db.query(UserBalance).filter(UserBalance.user_id == user_id).first()
                if not balance or balance.besitos < min_besitos:
                    missing.append(f"{min_besitos} besitos")
            except Exception as e:
                logger.error(f"Failed to check besitos for user {user_id}: {e}")
                missing.append(f"{min_besitos} besitos")
            finally:
                db.close()
        
        # Check completed fragments requirement
        if "required_fragments" in conditions:
            db: Session = next(get_db())
            try:
                for fragment_key in conditions["required_fragments"]:
                    progress = db.query(UserNarrativeProgress).join(
                        UserNarrativeProgress.fragment
                    ).filter(
                        UserNarrativeProgress.user_id == user_id,
                        UserNarrativeProgress.fragment.has(fragment_key=fragment_key)
                    ).first()
                    
                    if not progress:
                        missing.append(f"completar fragmento {fragment_key}")
            except Exception as e:
                logger.error(f"Failed to check fragment requirements for user {user_id}: {e}")
                missing.append("completar fragmentos requeridos")
            finally:
                db.close()
        
        # Check item requirement
        if "required_items" in conditions:
            missing.append("items especiales")
        
        # Check subscription requirement
        if "subscription" in conditions:
            missing.append(f"suscripción {conditions['subscription']}")
        
        # Check narrative flags
        if "narrative_flags" in conditions:
            missing.append("progreso narrativo específico")
        
        return missing
    
    def check_unlock_status(self, user_id: int, fragment_key: str) -> Dict[str, Any]:
        """
        Check unlock status for a specific fragment
        
        Args:
            user_id: User ID
            fragment_key: Fragment identifier
            
        Returns:
            dict: Unlock status with details
        """
        db: Session = next(get_db())
        
        try:
            # Get fragment and its unlock conditions
            from database.models import NarrativeFragment
            fragment = db.query(NarrativeFragment).filter(
                NarrativeFragment.fragment_key == fragment_key
            ).first()
            
            if not fragment:
                return {
                    "unlocked": False,
                    "reason": "Fragmento no encontrado"
                }
            
            # Check if already completed
            progress = db.query(UserNarrativeProgress).filter(
                UserNarrativeProgress.user_id == user_id,
                UserNarrativeProgress.fragment_id == fragment.id
            ).first()
            
            if progress:
                return {
                    "unlocked": True,
                    "reason": "Ya completado",
                    "completed": True
                }
            
            # Check unlock conditions
            conditions = fragment.unlock_conditions
            is_unlocked = self.evaluate_conditions(user_id, conditions)
            
            if is_unlocked:
                return {
                    "unlocked": True,
                    "reason": "Condiciones cumplidas",
                    "completed": False
                }
            else:
                missing = self.get_missing_requirements(user_id, conditions)
                return {
                    "unlocked": False,
                    "reason": "Condiciones no cumplidas",
                    "missing_requirements": missing,
                    "completed": False
                }
                
        except Exception as e:
            logger.error(f"Failed to check unlock status for fragment {fragment_key}: {e}")
            return {
                "unlocked": False,
                "reason": f"Error: {str(e)}"
            }
        finally:
            db.close()