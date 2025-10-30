"""
Enhanced Narrative Engine with MongoDB integration
"""

import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from database.connection import get_db, get_mongo
from database.models import NarrativeLevel, NarrativeFragment, UserNarrativeProgress, User
from modules.narrative.unlocks import UnlockEngine

logger = logging.getLogger(__name__)


class NarrativeEngine:
    """Enhanced engine for managing interactive narratives with MongoDB content"""
    
    def __init__(self):
        self.mongo_db = get_mongo()
        self.narrative_content = self.mongo_db.narrative_content
        self.user_states = self.mongo_db.user_narrative_states
        self.unlock_engine = UnlockEngine()
    
    @staticmethod
    def get_available_levels(user: User) -> List[NarrativeLevel]:
        """
        Get narrative levels available to user based on unlock conditions
        
        Args:
            user: User object
            
        Returns:
            list: Available levels
        """
        db: Session = next(get_db())
        
        try:
            levels = db.query(NarrativeLevel).filter(
                NarrativeLevel.is_active == True
            ).order_by(NarrativeLevel.order_index).all()
            
            available_levels = []
            
            for level in levels:
                # Check if level is unlocked for user
                is_unlocked = NarrativeEngine._check_unlock_conditions(user.id, level.unlock_conditions)
                
                if is_unlocked:
                    available_levels.append(level)
            
            return available_levels
            
        except Exception as e:
            logger.error(f"Failed to get available levels for user {user.id}: {e}")
            return []
        finally:
            db.close()
    
    def get_fragment_content(self, fragment_key: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed fragment content from MongoDB
        
        Args:
            fragment_key: Fragment identifier
            
        Returns:
            dict: Fragment content with decisions, or None if not found
        """
        try:
            content = self.narrative_content.find_one({"fragment_key": fragment_key})
            if content:
                # Remove MongoDB _id field
                content.pop("_id", None)
                return content
            return None
        except Exception as e:
            logger.error(f"Failed to get fragment content for {fragment_key}: {e}")
            return None
    
    def get_available_decisions(self, user_id: int, fragment_key: str) -> List[Dict[str, Any]]:
        """
        Get available decisions for a fragment, filtered by user state
        
        Args:
            user_id: User ID
            fragment_key: Fragment identifier
            
        Returns:
            list: Available decisions with consequences
        """
        try:
            fragment_content = self.get_fragment_content(fragment_key)
            if not fragment_content or "content" not in fragment_content:
                return []
            
            content = fragment_content["content"]
            decisions = content.get("decisions", [])
            
            # Get user state for condition evaluation
            user_state = self.get_user_narrative_state(user_id)
            
            available_decisions = []
            for decision in decisions:
                if self._check_decision_visibility(user_state, decision):
                    available_decisions.append(decision)
            
            return available_decisions
            
        except Exception as e:
            logger.error(f"Failed to get available decisions for user {user_id}: {e}")
            return []
    
    def process_decision(self, user_id: int, fragment_key: str, decision_id: str) -> Optional[Dict[str, Any]]:
        """
        Process user decision and apply consequences
        
        Args:
            user_id: User ID
            fragment_key: Current fragment
            decision_id: Selected decision
            
        Returns:
            dict: Next fragment details and rewards, or None if failed
        """
        try:
            # Get decision details
            decisions = self.get_available_decisions(user_id, fragment_key)
            selected_decision = next((d for d in decisions if d["decision_id"] == decision_id), None)
            
            if not selected_decision:
                logger.error(f"Decision {decision_id} not available for user {user_id}")
                return None
            
            consequences = selected_decision.get("consequences", {})
            
            # Apply immediate consequences
            rewards = consequences.get("immediate_rewards", {})
            narrative_flags = consequences.get("narrative_flags", [])
            next_fragment = consequences.get("next_fragment")
            
            # Update user state
            self._update_user_narrative_state(user_id, narrative_flags, rewards)
            
            # Record progress in PostgreSQL
            self._record_progress(user_id, fragment_key, decision_id)
            
            # Get next fragment details
            if next_fragment:
                next_fragment_details = self.get_fragment_content(next_fragment)
                if next_fragment_details:
                    return {
                        "next_fragment": next_fragment_details,
                        "rewards": rewards,
                        "narrative_flags": narrative_flags
                    }
            
            return {
                "next_fragment": None,
                "rewards": rewards,
                "narrative_flags": narrative_flags
            }
            
        except Exception as e:
            logger.error(f"Failed to process decision for user {user_id}: {e}")
            return None
    
    def get_user_narrative_state(self, user_id: int) -> Dict[str, Any]:
        """
        Get user's narrative state from MongoDB
        
        Args:
            user_id: User ID
            
        Returns:
            dict: User narrative state
        """
        try:
            state = self.user_states.find_one({"user_id": user_id})
            if state:
                state.pop("_id", None)
                return state
            
            # Create default state if not exists
            default_state = {
                "user_id": user_id,
                "narrative_flags": [],
                "variables": {},
                "completed_fragments": [],
                "total_besitos_earned": 0
            }
            self.user_states.insert_one(default_state.copy())
            return default_state
            
        except Exception as e:
            logger.error(f"Failed to get narrative state for user {user_id}: {e}")
            return {"user_id": user_id, "narrative_flags": [], "variables": {}}
    
    def _update_user_narrative_state(self, user_id: int, narrative_flags: List[str], rewards: Dict[str, Any]):
        """Update user narrative state with new flags and rewards"""
        try:
            current_state = self.get_user_narrative_state(user_id)
            
            # Add new flags
            current_flags = current_state.get("narrative_flags", [])
            for flag in narrative_flags:
                if flag not in current_flags:
                    current_flags.append(flag)
            
            # Update rewards
            if "besitos" in rewards:
                current_state["total_besitos_earned"] = current_state.get("total_besitos_earned", 0) + rewards["besitos"]
            
            # Update in MongoDB
            self.user_states.update_one(
                {"user_id": user_id},
                {"$set": {
                    "narrative_flags": current_flags,
                    "total_besitos_earned": current_state.get("total_besitos_earned", 0)
                }}
            )
            
        except Exception as e:
            logger.error(f"Failed to update narrative state for user {user_id}: {e}")
    
    def _check_decision_visibility(self, user_state: Dict[str, Any], decision: Dict[str, Any]) -> bool:
        """Check if decision should be visible to user based on conditions"""
        visible_if = decision.get("visible_if")
        if not visible_if:
            return True
        
        # Check item requirements
        if "has_item" in visible_if:
            required_item = visible_if["has_item"]
            # TODO: Integrate with inventory system
            # For now, assume user has the item
            pass
        
        # Check narrative flags
        if "narrative_flags" in visible_if:
            required_flags = visible_if["narrative_flags"]
            user_flags = user_state.get("narrative_flags", [])
            for flag in required_flags:
                if flag not in user_flags:
                    return False
        
        # Check variable conditions
        if "variables" in visible_if:
            for var_name, condition in visible_if["variables"].items():
                user_value = user_state.get("variables", {}).get(var_name, 0)
                if not self._evaluate_condition(user_value, condition):
                    return False
        
        return True
    
    def _evaluate_condition(self, value: Any, condition: str) -> bool:
        """Evaluate condition string (e.g., '>= 5', '== true')"""
        try:
            if condition.startswith(">="):
                return value >= float(condition[2:].strip())
            elif condition.startswith("<="):
                return value <= float(condition[2:].strip())
            elif condition.startswith(">"):
                return value > float(condition[1:].strip())
            elif condition.startswith("<"):
                return value < float(condition[1:].strip())
            elif condition.startswith("=="):
                return str(value) == condition[2:].strip()
            elif condition.startswith("!="):
                return str(value) != condition[2:].strip()
            else:
                return bool(value)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def _record_progress(user_id: int, fragment_key: str, decision_id: str):
        """Record user progress in PostgreSQL"""
        db: Session = next(get_db())
        
        try:
            # Get fragment
            fragment = db.query(NarrativeFragment).filter(
                NarrativeFragment.fragment_key == fragment_key
            ).first()
            
            if fragment:
                # Check if progress already exists
                progress = db.query(UserNarrativeProgress).filter(
                    UserNarrativeProgress.user_id == user_id,
                    UserNarrativeProgress.fragment_id == fragment.id
                ).first()
                
                if progress:
                    # Update existing progress
                    choices = progress.choices_made or {}
                    choices[decision_id] = {"timestamp": "now"}  # TODO: Add actual timestamp
                    progress.choices_made = choices
                else:
                    # Create new progress
                    progress = UserNarrativeProgress(
                        user_id=user_id,
                        fragment_id=fragment.id,
                        choices_made={decision_id: {"timestamp": "now"}}
                    )
                    db.add(progress)
                
                db.commit()
                
        except Exception as e:
            logger.error(f"Failed to record progress for user {user_id}: {e}")
            db.rollback()
        finally:
            db.close()
    
    @staticmethod
    def _check_unlock_conditions(user_id: int, conditions: Optional[Dict[str, Any]]) -> bool:
        """Check if user meets unlock conditions"""
        if not conditions:
            return True
        
        # Check besitos requirement
        if "min_besitos" in conditions:
            # TODO: Integrate with besitos system
            # For now, assume user has enough besitos
            pass
        
        # Check items requirement
        if "required_items" in conditions:
            # TODO: Integrate with inventory system
            # For now, assume user has required items
            pass
        
        # Check previous fragments requirement
        if "required_fragments" in conditions:
            db: Session = next(get_db())
            try:
                for fragment_key in conditions["required_fragments"]:
                    fragment = db.query(NarrativeFragment).filter(
                        NarrativeFragment.fragment_key == fragment_key
                    ).first()
                    if fragment:
                        progress = db.query(UserNarrativeProgress).filter(
                            UserNarrativeProgress.user_id == user_id,
                            UserNarrativeProgress.fragment_id == fragment.id
                        ).first()
                        if not progress:
                            return False
            finally:
                db.close()
        
        return True
    
    def start_story(self, user: User, level_key: str) -> Optional[Dict[str, Any]]:
        """Start a new story for user
        
        Args:
            user: User object
            level_key: Level identifier
            
        Returns:
            dict: First fragment details, or None if failed
        """
        db: Session = next(get_db())
        
        try:
            # Get level
            level = db.query(NarrativeLevel).filter(
                NarrativeLevel.level_key == level_key
            ).first()
            
            if not level:
                logger.error(f"Level {level_key} not found")
                return None
            
            # Get first fragment for this level (lowest order_index)
            first_fragment = db.query(NarrativeFragment).filter(
                NarrativeFragment.level_id == level.id
            ).order_by(NarrativeFragment.order_index.asc()).first()
            
            if not first_fragment:
                logger.error(f"No fragments found for level {level_key}")
                return None
            
            # Record user progress
            progress = UserNarrativeProgress(
                user_id=user.id,
                fragment_id=first_fragment.id,
                choices_made={}
            )
            db.add(progress)
            db.commit()
            
            # Return fragment details
            return {
                "fragment_key": first_fragment.fragment_key,
                "title": first_fragment.title,
                "description": first_fragment.title  # Usar title como description temporalmente
            }
            
        except Exception as e:
            logger.error(f"Failed to start story for user {user.id}: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def get_current_progress(self, user: User) -> Optional[Dict[str, Any]]:
        """Get user's current narrative progress
        
        Args:
            user: User object
            
        Returns:
            dict: Current fragment details, or None if no progress
        """
        db: Session = next(get_db())
        
        try:
            # Get latest progress
            progress = db.query(UserNarrativeProgress).filter(
                UserNarrativeProgress.user_id == user.id
            ).order_by(UserNarrativeProgress.updated_at.desc()).first()
            
            if not progress:
                return None
            
            fragment = progress.fragment
            
            return {
                "fragment_key": fragment.fragment_key,
                "title": fragment.title,
                "description": fragment.title  # Usar title como description temporalmente
            }
            
        except Exception as e:
            logger.error(f"Failed to get current progress for user {user.id}: {e}")
            return None
        finally:
            db.close()
    
    def check_fragment_access(self, user_id: int, fragment_key: str) -> Dict[str, Any]:
        """
        Check if user can access a fragment
        
        Args:
            user_id: User ID
            fragment_key: Fragment identifier
            
        Returns:
            dict: Access status with details
        """
        return self.unlock_engine.check_unlock_status(user_id, fragment_key)
    
    def get_accessible_fragments(self, user_id: int, level_key: str) -> List[Dict[str, Any]]:
        """
        Get all fragments accessible to user in a level
        
        Args:
            user_id: User ID
            level_key: Level identifier
            
        Returns:
            list: Accessible fragments with status
        """
        db: Session = next(get_db())
        
        try:
            # Get level
            level = db.query(NarrativeLevel).filter(
                NarrativeLevel.level_key == level_key
            ).first()
            
            if not level:
                return []
            
            # Get all fragments for this level
            fragments = db.query(NarrativeFragment).filter(
                NarrativeFragment.level_id == level.id
            ).order_by(NarrativeFragment.order_index).all()
            
            accessible_fragments = []
            
            for fragment in fragments:
                access_status = self.check_fragment_access(user_id, fragment.fragment_key)
                
                accessible_fragments.append({
                    "fragment_key": fragment.fragment_key,
                    "title": fragment.title,
                    "description": fragment.title,  # Using title as description temporarily
                    "order_index": fragment.order_index,
                    "access_status": access_status
                })
            
            return accessible_fragments
            
        except Exception as e:
            logger.error(f"Failed to get accessible fragments for user {user_id}: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def _get_next_fragments(current_fragment_key: str) -> List[Dict[str, Any]]:
        """Get next available fragments based on current fragment"""
        # Simple mapping for fragment connections
        fragment_connections = {
            "fragment_1_1": [
                {"key": "fragment_1_2", "title": "Continuar explorando", "description": "Avanza en tu aventura"}
            ],
            "fragment_1_2": [
                {"key": "fragment_1_3", "title": "Seguir adelante", "description": "Descubre qué hay más allá"}
            ],
            "fragment_1_3": [
                {"key": "level_1_end", "title": "Completar nivel", "description": "Finaliza esta parte de la historia"}
            ],
            "level_1_end": [
                {"key": "fragment_2_1", "title": "Continuar al Nivel 2", "description": "Nuevos misterios te esperan"}
            ],
            "fragment_2_1": [
                {"key": "level_2_end", "title": "Final del Nivel 2", "description": "Has completado el nivel"}
            ],
            "level_2_end": [
                {"key": "intro_3", "title": "Continuar al Nivel 3", "description": "El ático prohibido"}
            ]
        }
        
        return fragment_connections.get(current_fragment_key, [])