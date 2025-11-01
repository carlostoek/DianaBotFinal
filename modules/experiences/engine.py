"""
Motor de Experiencias Unificadas

Este módulo implementa el motor central para gestionar experiencias que integran
múltiples elementos de diferentes sistemas en flujos cohesivos.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from database.connection import get_db
from database.models import (
    Experience, ExperienceComponent, UserExperienceProgress, 
    UserComponentCompletion, ExperienceRequirement, ExperienceReward
)

logger = logging.getLogger(__name__)


class ExperienceEngine:
    """Motor principal para gestionar experiencias unificadas"""
    
    def __init__(self):
        self.db = next(get_db())
    
    def start_experience(self, user_id: int, experience_id: int) -> Dict[str, Any]:
        """
        Iniciar una experiencia para un usuario
        
        Args:
            user_id: ID del usuario
            experience_id: ID de la experiencia
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validar requisitos compuestos
            can_start, missing_reqs = self._validate_requirements(user_id, experience_id)
            if not can_start:
                return {
                    'success': False,
                    'error': 'requirements_not_met',
                    'missing_requirements': missing_reqs
                }
            
            # Verificar si ya existe progreso
            existing_progress = self.db.query(UserExperienceProgress).filter(
                UserExperienceProgress.user_id == user_id,
                UserExperienceProgress.experience_id == experience_id
            ).first()
            
            if existing_progress:
                if existing_progress.status == 'completed':
                    return {
                        'success': False,
                        'error': 'experience_already_completed'
                    }
                elif existing_progress.status == 'in_progress':
                    return {
                        'success': True,
                        'status': 'resumed',
                        'progress': existing_progress
                    }
            
            # Obtener primer componente
            first_component = self.db.query(ExperienceComponent).filter(
                ExperienceComponent.experience_id == experience_id,
                ExperienceComponent.sequence_order == 1
            ).first()
            
            if not first_component:
                return {
                    'success': False,
                    'error': 'no_components_found'
                }
            
            # Crear progreso de usuario
            user_progress = UserExperienceProgress(
                user_id=user_id,
                experience_id=experience_id,
                status='in_progress',
                current_component_id=first_component.id,
                started_at=datetime.utcnow(),
                last_activity_at=datetime.utcnow(),
                completion_percentage=0.0,
                components_completed=0,
                components_total=self._get_total_components(experience_id)
            )
            
            self.db.add(user_progress)
            self.db.commit()
            
            # Actualizar contador de inicios
            experience = self.db.query(Experience).filter(Experience.id == experience_id).first()
            if experience:
                experience.start_count += 1
                self.db.commit()
            
            logger.info(f"Experiencia {experience_id} iniciada para usuario {user_id}")
            
            return {
                'success': True,
                'status': 'started',
                'progress': user_progress,
                'current_component': first_component
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al iniciar experiencia: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def progress_experience(self, user_id: int, experience_id: int, component_id: int, 
                          completion_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Progresar en una experiencia marcando un componente como completado
        
        Args:
            user_id: ID del usuario
            experience_id: ID de la experiencia
            component_id: ID del componente completado
            completion_data: Datos adicionales de completitud
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Obtener progreso actual
            user_progress = self.db.query(UserExperienceProgress).filter(
                UserExperienceProgress.user_id == user_id,
                UserExperienceProgress.experience_id == experience_id
            ).first()
            
            if not user_progress or user_progress.status != 'in_progress':
                return {
                    'success': False,
                    'error': 'experience_not_in_progress'
                }
            
            # Verificar que el componente es el actual o está disponible
            component = self.db.query(ExperienceComponent).filter(
                ExperienceComponent.id == component_id
            ).first()
            
            if not component:
                return {
                    'success': False,
                    'error': 'component_not_found'
                }
            
            # Verificar si ya está completado
            existing_completion = self.db.query(UserComponentCompletion).filter(
                UserComponentCompletion.user_progress_id == user_progress.id,
                UserComponentCompletion.component_id == component_id
            ).first()
            
            if existing_completion:
                return {
                    'success': False,
                    'error': 'component_already_completed'
                }
            
            # Registrar completitud del componente
            component_completion = UserComponentCompletion(
                user_progress_id=user_progress.id,
                component_id=component_id,
                completed_at=datetime.utcnow(),
                completion_data=completion_data or {}
            )
            
            self.db.add(component_completion)
            
            # Actualizar progreso
            user_progress.components_completed += 1
            user_progress.last_activity_at = datetime.utcnow()
            
            # Calcular porcentaje de completitud
            total_components = user_progress.components_total
            if total_components > 0:
                user_progress.completion_percentage = (user_progress.components_completed / total_components) * 100
            
            # Otorgar recompensas del componente
            if component.completion_rewards:
                self._grant_component_rewards(user_id, component.completion_rewards)
            
            # Determinar siguiente componente
            next_component = self._get_next_component(experience_id, component.sequence_order)
            if next_component:
                user_progress.current_component_id = next_component.id
            else:
                # No hay más componentes, completar experiencia
                return self.complete_experience(user_id, experience_id)
            
            self.db.commit()
            
            logger.info(f"Componente {component_id} completado en experiencia {experience_id} por usuario {user_id}")
            
            return {
                'success': True,
                'component_completed': component,
                'next_component': next_component,
                'progress': user_progress
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al progresar experiencia: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def complete_experience(self, user_id: int, experience_id: int) -> Dict[str, Any]:
        """
        Completar una experiencia
        
        Args:
            user_id: ID del usuario
            experience_id: ID de la experiencia
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Obtener progreso actual
            user_progress = self.db.query(UserExperienceProgress).filter(
                UserExperienceProgress.user_id == user_id,
                UserExperienceProgress.experience_id == experience_id
            ).first()
            
            if not user_progress:
                return {
                    'success': False,
                    'error': 'experience_not_found'
                }
            
            # Actualizar progreso
            user_progress.status = 'completed'
            user_progress.completed_at = datetime.utcnow()
            user_progress.completion_percentage = 100.0
            user_progress.last_activity_at = datetime.utcnow()
            
            # Otorgar recompensas finales
            experience_rewards = self.db.query(ExperienceReward).filter(
                ExperienceReward.experience_id == experience_id
            ).all()
            
            rewards_granted = []
            for reward in experience_rewards:
                reward_result = self._grant_experience_reward(user_id, reward)
                rewards_granted.append({
                    'reward': reward,
                    'result': reward_result
                })
            
            # Actualizar contador de completitudes
            experience = self.db.query(Experience).filter(Experience.id == experience_id).first()
            if experience:
                experience.completion_count += 1
                # Calcular tiempo promedio de completitud
                if user_progress.started_at and user_progress.completed_at:
                    completion_time = (user_progress.completed_at - user_progress.started_at).total_seconds() / 60
                    if experience.average_completion_time == 0:
                        experience.average_completion_time = completion_time
                    else:
                        experience.average_completion_time = (
                            experience.average_completion_time + completion_time
                        ) / 2
            
            self.db.commit()
            
            logger.info(f"Experiencia {experience_id} completada por usuario {user_id}")
            
            return {
                'success': True,
                'progress': user_progress,
                'rewards_granted': rewards_granted
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al completar experiencia: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_experience_status(self, user_id: int, experience_id: int) -> Dict[str, Any]:
        """
        Obtener estado actual de una experiencia para un usuario
        
        Args:
            user_id: ID del usuario
            experience_id: ID de la experiencia
            
        Returns:
            Dict con estado de la experiencia
        """
        try:
            # Obtener progreso del usuario
            user_progress = self.db.query(UserExperienceProgress).filter(
                UserExperienceProgress.user_id == user_id,
                UserExperienceProgress.experience_id == experience_id
            ).first()
            
            # Obtener experiencia
            experience = self.db.query(Experience).filter(Experience.id == experience_id).first()
            
            if not experience:
                return {
                    'success': False,
                    'error': 'experience_not_found'
                }
            
            # Si no hay progreso, verificar requisitos
            if not user_progress:
                can_start, missing_reqs = self._validate_requirements(user_id, experience_id)
                return {
                    'success': True,
                    'status': 'not_started',
                    'can_start': can_start,
                    'missing_requirements': missing_reqs,
                    'experience': experience
                }
            
            # Obtener componentes completados
            completed_components = self.db.query(UserComponentCompletion).filter(
                UserComponentCompletion.user_progress_id == user_progress.id
            ).all()
            
            # Obtener componente actual
            current_component = None
            if user_progress.current_component_id:
                current_component = self.db.query(ExperienceComponent).filter(
                    ExperienceComponent.id == user_progress.current_component_id
                ).first()
            
            return {
                'success': True,
                'status': user_progress.status,
                'progress': user_progress,
                'current_component': current_component,
                'completed_components': completed_components,
                'experience': experience
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estado de experiencia: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_requirements(self, user_id: int, experience_id: int) -> tuple[bool, List[Dict]]:
        """Validar requisitos compuestos para iniciar experiencia"""
        requirements = self.db.query(ExperienceRequirement).filter(
            ExperienceRequirement.experience_id == experience_id
        ).all()
        
        missing_requirements = []
        all_met = True
        
        for req in requirements:
            is_met, details = self._check_requirement(user_id, req)
            if not is_met:
                all_met = False
                missing_requirements.append({
                    'requirement': req,
                    'details': details
                })
        
        return all_met, missing_requirements
    
    def _check_requirement(self, user_id: int, requirement: ExperienceRequirement) -> tuple[bool, Dict]:
        """Verificar un requisito específico"""
        # TODO: Implementar validación específica por tipo de requisito
        # Por ahora retornamos True para todos los requisitos
        return True, {}
    
    def _get_total_components(self, experience_id: int) -> int:
        """Obtener número total de componentes en una experiencia"""
        return self.db.query(ExperienceComponent).filter(
            ExperienceComponent.experience_id == experience_id
        ).count()
    
    def _get_next_component(self, experience_id: int, current_order: int) -> Optional[ExperienceComponent]:
        """Obtener siguiente componente en la secuencia"""
        return self.db.query(ExperienceComponent).filter(
            ExperienceComponent.experience_id == experience_id,
            ExperienceComponent.sequence_order > current_order
        ).order_by(ExperienceComponent.sequence_order.asc()).first()
    
    def _grant_component_rewards(self, user_id: int, rewards: Dict) -> bool:
        """Otorgar recompensas de componente"""
        # TODO: Implementar otorgamiento de recompensas
        return True
    
    def _grant_experience_reward(self, user_id: int, reward: ExperienceReward) -> bool:
        """Otorgar recompensa de experiencia"""
        # TODO: Implementar otorgamiento de recompensas
        return True