"""
Validador de Requisitos Compuestos

Este módulo implementa la validación de requisitos que integran múltiples sistemas
para determinar si un usuario puede iniciar o progresar en una experiencia.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging

from sqlalchemy.orm import Session
from database.models import (
    User, UserBalance, UserInventory, UserAchievement, 
    ExperienceRequirement, VIPSubscription
)

logger = logging.getLogger(__name__)


class CompositeValidator:
    """Validador de requisitos compuestos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_composite_requirements(self, user_id: int, requirements: List[Dict]) -> Dict[str, Any]:
        """
        Validar múltiples requisitos de diferentes sistemas
        
        Args:
            user_id: ID del usuario
            requirements: Lista de requisitos a validar
            
        Returns:
            Dict con resultado de validación
        """
        validation_results = []
        all_valid = True
        
        for req in requirements:
            is_valid, details = self._validate_single_requirement(user_id, req)
            validation_results.append({
                'requirement': req,
                'is_valid': is_valid,
                'details': details
            })
            
            if not is_valid:
                all_valid = False
        
        return {
            'all_valid': all_valid,
            'validation_results': validation_results
        }
    
    def can_start_experience(self, user_id: int, experience_id: int) -> Tuple[bool, List[Dict]]:
        """
        Verificar si un usuario puede iniciar una experiencia
        
        Args:
            user_id: ID del usuario
            experience_id: ID de la experiencia
            
        Returns:
            Tuple (puede_iniciar, requisitos_faltantes)
        """
        # Obtener requisitos de la experiencia
        requirements = self.db.query(ExperienceRequirement).filter(
            ExperienceRequirement.experience_id == experience_id
        ).all()
        
        missing_requirements = []
        can_start = True
        
        for req in requirements:
            is_met, details = self._check_experience_requirement(user_id, req)
            if not is_met:
                can_start = False
                missing_requirements.append({
                    'requirement': req,
                    'details': details
                })
        
        return can_start, missing_requirements
    
    def get_missing_requirements(self, user_id: int, experience_id: int) -> List[Dict]:
        """
        Obtener lista detallada de requisitos faltantes
        
        Args:
            user_id: ID del usuario
            experience_id: ID de la experiencia
            
        Returns:
            Lista de requisitos faltantes con detalles
        """
        _, missing_reqs = self.can_start_experience(user_id, experience_id)
        return missing_reqs
    
    def _validate_single_requirement(self, user_id: int, requirement: Dict) -> Tuple[bool, Dict]:
        """Validar un requisito individual"""
        req_type = requirement.get('type')
        req_value = requirement.get('value', {})
        
        if req_type == 'level':
            return self._validate_level_requirement(user_id, req_value)
        elif req_type == 'vip_membership':
            return self._validate_vip_requirement(user_id, req_value)
        elif req_type == 'item':
            return self._validate_item_requirement(user_id, req_value)
        elif req_type == 'achievement':
            return self._validate_achievement_requirement(user_id, req_value)
        elif req_type == 'experience_completed':
            return self._validate_experience_requirement(user_id, req_value)
        elif req_type == 'besitos':
            return self._validate_besitos_requirement(user_id, req_value)
        else:
            logger.warning(f"Tipo de requisito desconocido: {req_type}")
            return False, {'error': 'unknown_requirement_type'}
    
    def _check_experience_requirement(self, user_id: int, requirement: ExperienceRequirement) -> Tuple[bool, Dict]:
        """Verificar un requisito de experiencia específico"""
        req_type = requirement.requirement_type
        req_value = requirement.requirement_value
        
        if req_type == 'level':
            return self._validate_level_requirement(user_id, req_value)
        elif req_type == 'vip_membership':
            return self._validate_vip_requirement(user_id, req_value)
        elif req_type == 'item':
            return self._validate_item_requirement(user_id, req_value)
        elif req_type == 'achievement':
            return self._validate_achievement_requirement(user_id, req_value)
        elif req_type == 'experience_completed':
            return self._validate_experience_requirement(user_id, req_value)
        elif req_type == 'besitos':
            return self._validate_besitos_requirement(user_id, req_value)
        else:
            logger.warning(f"Tipo de requisito desconocido: {req_type}")
            return False, {'error': 'unknown_requirement_type'}
    
    def _validate_level_requirement(self, user_id: int, requirement_value: Dict) -> Tuple[bool, Dict]:
        """Validar requisito de nivel"""
        min_level = requirement_value.get('min_level', 1)
        
        # TODO: Implementar sistema de niveles
        # Por ahora asumimos nivel 1 para todos los usuarios
        user_level = 1
        
        is_met = user_level >= min_level
        details = {
            'required_level': min_level,
            'current_level': user_level,
            'missing_levels': max(0, min_level - user_level)
        }
        
        return is_met, details
    
    def _validate_vip_requirement(self, user_id: int, requirement_value: Dict) -> Tuple[bool, Dict]:
        """Validar requisito de membresía VIP"""
        required = requirement_value.get('required', False)
        
        if not required:
            return True, {'vip_required': False}
        
        # Verificar suscripción VIP activa
        vip_subscription = self.db.query(VIPSubscription).filter(
            VIPSubscription.user_id == user_id,
            VIPSubscription.is_active
        ).first()
        
        is_met = vip_subscription is not None
        details = {
            'vip_required': True,
            'has_vip': is_met
        }
        
        return is_met, details
    
    def _validate_item_requirement(self, user_id: int, requirement_value: Dict) -> Tuple[bool, Dict]:
        """Validar requisito de items"""
        item_ids = requirement_value.get('item_ids', [])
        all_required = requirement_value.get('all_required', True)
        
        if not item_ids:
            return True, {'items_required': False}
        
        # Verificar items en inventario
        user_items = self.db.query(UserInventory).filter(
            UserInventory.user_id == user_id,
            UserInventory.item_id.in_(item_ids)
        ).all()
        
        owned_item_ids = [item.item_id for item in user_items]
        
        if all_required:
            is_met = set(item_ids).issubset(set(owned_item_ids))
            missing_items = list(set(item_ids) - set(owned_item_ids))
        else:
            is_met = len(set(item_ids) & set(owned_item_ids)) > 0
            missing_items = [] if is_met else item_ids
        
        details = {
            'required_items': item_ids,
            'owned_items': owned_item_ids,
            'all_required': all_required,
            'missing_items': missing_items
        }
        
        return is_met, details
    
    def _validate_achievement_requirement(self, user_id: int, requirement_value: Dict) -> Tuple[bool, Dict]:
        """Validar requisito de logros"""
        achievement_ids = requirement_value.get('achievement_ids', [])
        
        if not achievement_ids:
            return True, {'achievements_required': False}
        
        # Verificar logros desbloqueados
        user_achievements = self.db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id.in_(achievement_ids)
        ).all()
        
        unlocked_achievement_ids = [ua.achievement_id for ua in user_achievements]
        missing_achievements = list(set(achievement_ids) - set(unlocked_achievement_ids))
        
        is_met = len(missing_achievements) == 0
        details = {
            'required_achievements': achievement_ids,
            'unlocked_achievements': unlocked_achievement_ids,
            'missing_achievements': missing_achievements
        }
        
        return is_met, details
    
    def _validate_experience_requirement(self, user_id: int, requirement_value: Dict) -> Tuple[bool, Dict]:
        """Validar requisito de experiencias completadas"""
        experience_ids = requirement_value.get('experience_ids', [])
        
        if not experience_ids:
            return True, {'experiences_required': False}
        
        # TODO: Implementar verificación de experiencias completadas
        # Por ahora asumimos que no se han completado experiencias
        completed_experiences = []
        missing_experiences = experience_ids
        
        is_met = len(missing_experiences) == 0
        details = {
            'required_experiences': experience_ids,
            'completed_experiences': completed_experiences,
            'missing_experiences': missing_experiences
        }
        
        return is_met, details
    
    def _validate_besitos_requirement(self, user_id: int, requirement_value: Dict) -> Tuple[bool, Dict]:
        """Validar requisito de besitos"""
        min_besitos = requirement_value.get('min_besitos', 0)
        
        if min_besitos <= 0:
            return True, {'besitos_required': False}
        
        # Obtener balance de besitos
        user_balance = self.db.query(UserBalance).filter(
            UserBalance.user_id == user_id
        ).first()
        
        current_besitos = user_balance.besitos if user_balance else 0
        
        is_met = current_besitos >= min_besitos
        details = {
            'required_besitos': min_besitos,
            'current_besitos': current_besitos,
            'missing_besitos': max(0, min_besitos - current_besitos)
        }
        
        return is_met, details