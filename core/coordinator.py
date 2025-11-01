"""
Coordinador Central para DianaBot

Sistema de coordinación que extiende Event Bus con capacidades de orquestación,
validación compuesta y transacciones distribuidas.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from core.event_bus import event_bus
from core.transaction_manager import transaction_manager

logger = logging.getLogger(__name__)


class ValidationResult:
    """Resultado de validación de requisitos compuestos"""
    
    def __init__(self, is_valid: bool, missing: Optional[List[str]] = None, suggestions: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.missing = missing or []
        self.suggestions = suggestions or []


class CoordinadorCentral:
    """
    Sistema de coordinación que extiende Event Bus con capacidades de orquestación
    """
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.validators = {}  # Validadores por tipo de acción
        self.orchestrators = {}  # Orquestadores de flujos
        self.transaction_manager = transaction_manager
        
        # Registrar validadores por defecto
        self._register_default_validators()
    
    def TOMAR_DECISION(self, user_id: int, fragment_id: int, decision_id: int) -> Dict[str, Any]:
        """
        Coordina toma de decisión narrativa con validación compuesta
        
        Flujo:
        1. Validar requisitos compuestos (narrativa + gamificación + admin + commerce)
        2. Si válido: aplicar decisión
        3. Otorgar recompensas en múltiples sistemas
        4. Actualizar progreso de experiencias relacionadas
        5. Emitir eventos a todos los sistemas afectados
        6. Si falla: rollback completo
        
        Args:
            user_id: ID del usuario
            fragment_id: ID del fragmento narrativo
            decision_id: ID de la decisión tomada
            
        Returns:
            Dict con resultado de la operación
        """
        with self.transaction_manager.begin() as tx:
            # Paso 1: Validar requisitos compuestos
            validation = self._validate_composite_requirements(
                user_id, 
                fragment_id,
                requirement_types=['narrative', 'vip', 'items', 'level']
            )
            
            if not validation.is_valid:
                # Emitir evento de acceso denegado
                self.event_bus.publish('coordinator.access_denied', {
                    'user_id': user_id,
                    'fragment_id': fragment_id,
                    'decision_id': decision_id,
                    'missing_requirements': validation.missing,
                    'timestamp': datetime.now().isoformat()
                })
                
                return {
                    'success': False,
                    'missing_requirements': validation.missing,
                    'suggestions': self._get_requirement_suggestions(validation.missing)
                }
            
            # Paso 2: Aplicar decisión en narrativa
            narrative_result = tx.execute(
                'narrative.apply_decision',
                user_id=user_id,
                fragment_id=fragment_id,
                decision_id=decision_id
            )
            
            if not narrative_result.success:
                return {
                    'success': False,
                    'error': narrative_result.error
                }
            
            # Paso 3: Otorgar recompensas
            rewards = narrative_result.data.get('rewards', {})
            
            if rewards.get('besitos'):
                besitos_result = tx.execute(
                    'gamification.grant_besitos',
                    user_id=user_id,
                    amount=rewards['besitos'],
                    reason=f"Decisión narrativa {decision_id}"
                )
                
                if not besitos_result.success:
                    return {
                        'success': False,
                        'error': f"Error otorgando besitos: {besitos_result.error}"
                    }
            
            if rewards.get('items'):
                for item_id in rewards['items']:
                    inventory_result = tx.execute(
                        'gamification.add_to_inventory',
                        user_id=user_id,
                        item_id=item_id
                    )
                    
                    if not inventory_result.success:
                        return {
                            'success': False,
                            'error': f"Error agregando item al inventario: {inventory_result.error}"
                        }
            
            if rewards.get('unlock_content'):
                unlock_result = tx.execute(
                    'narrative.unlock_fragments',
                    user_id=user_id,
                    fragment_ids=rewards['unlock_content']
                )
                
                if not unlock_result.success:
                    return {
                        'success': False,
                        'error': f"Error desbloqueando fragmentos: {unlock_result.error}"
                    }
            
            # Paso 4: Actualizar experiencias relacionadas
            related_experiences = self._get_related_experiences(fragment_id)
            for exp_id in related_experiences:
                experience_result = tx.execute(
                    'experience.progress_component',
                    user_id=user_id,
                    experience_id=exp_id,
                    component_type='narrative',
                    component_id=fragment_id
                )
                
                if not experience_result.success:
                    logger.warning(f"Error actualizando experiencia {exp_id}: {experience_result.error}")
            
            # Paso 5: Emitir eventos
            tx.on_commit(lambda: self.event_bus.publish(
                'coordinator.decision_taken',
                {
                    'user_id': user_id,
                    'fragment_id': fragment_id,
                    'decision_id': decision_id,
                    'rewards': rewards,
                    'experiences_affected': related_experiences,
                    'timestamp': datetime.now().isoformat()
                }
            ))
            
            # Paso 6: Commit o rollback automático
            return {
                'success': True,
                'narrative_result': narrative_result.data,
                'rewards_granted': rewards,
                'experiences_updated': related_experiences
            }
    
    def ACCEDER_NARRATIVA_VIP(self, user_id: int, fragment_id: int) -> Dict[str, Any]:
        """
        Coordina acceso a contenido VIP con validación multi-nivel
        
        Flujo:
        1. Verificar membresía VIP activa
        2. Verificar acceso al canal VIP
        3. Validar requisitos adicionales del fragmento
        4. Si no tiene acceso: ofrecer upgrade
        5. Registrar intento de acceso para analytics
        6. Si tiene acceso: permitir y trackear
        
        Args:
            user_id: ID del usuario
            fragment_id: ID del fragmento VIP
            
        Returns:
            Dict con resultado del acceso
        """
        # Paso 1: Verificar membresía
        vip_result = self.transaction_manager.begin().execute(
            'admin.check_vip_membership',
            user_id=user_id
        )
        
        is_vip = vip_result.success and vip_result.data
        
        if not is_vip:
            # Registrar intento fallido
            self._track_conversion_opportunity(
                user_id, 
                'vip_content_access_denied',
                {'fragment_id': fragment_id}
            )
            
            # Generar oferta personalizada
            offer = self._generate_personalized_vip_offer(user_id)
            
            # Emitir evento de acceso denegado
            self.event_bus.publish('coordinator.access_denied', {
                'user_id': user_id,
                'fragment_id': fragment_id,
                'reason': 'vip_required',
                'offer_generated': offer is not None,
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': False,
                'reason': 'vip_required',
                'offer': offer,
                'preview': self._get_content_preview(fragment_id)
            }
        
        # Paso 2: Verificar acceso a canal
        channel_result = self.transaction_manager.begin().execute(
            'admin.verify_channel_membership',
            user_id=user_id,
            channel_type='VIP'
        )
        
        has_channel_access = channel_result.success and channel_result.data
        
        if not has_channel_access:
            # Caso raro: es VIP pero no está en canal
            fix_result = self.transaction_manager.begin().execute(
                'admin.fix_channel_membership',
                user_id=user_id
            )
            
            if not fix_result.success:
                logger.warning(f"No se pudo corregir membresía de canal para usuario {user_id}")
        
        # Paso 3: Validar requisitos adicionales
        additional_reqs = self._validate_fragment_requirements(
            user_id,
            fragment_id
        )
        
        if not additional_reqs.is_valid:
            self.event_bus.publish('coordinator.requirements_failed', {
                'user_id': user_id,
                'fragment_id': fragment_id,
                'missing_requirements': additional_reqs.missing,
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': False,
                'reason': 'additional_requirements',
                'missing': additional_reqs.missing
            }
        
        # Paso 4: Permitir acceso
        content_result = self.transaction_manager.begin().execute(
            'narrative.get_fragment_content',
            user_id=user_id,
            fragment_id=fragment_id
        )
        
        if not content_result.success:
            return {
                'success': False,
                'error': f"Error obteniendo contenido: {content_result.error}"
            }
        
        # Paso 5: Trackear acceso
        self.event_bus.publish('analytics.vip_content_accessed', {
            'user_id': user_id,
            'fragment_id': fragment_id,
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'success': True,
            'content': content_result.data,
            'vip_status': 'active'
        }
    
    def _validate_composite_requirements(self, user_id: int, fragment_id: int, 
                                       requirement_types: List[str]) -> ValidationResult:
        """
        Valida requisitos compuestos para acceso a fragmento
        
        Args:
            user_id: ID del usuario
            fragment_id: ID del fragmento
            requirement_types: Tipos de requisitos a validar
            
        Returns:
            ValidationResult con resultado de validación
        """
        missing_requirements = []
        
        for req_type in requirement_types:
            validator = self.validators.get(req_type)
            if validator:
                result = validator(user_id, fragment_id)
                if not result.is_valid:
                    missing_requirements.extend(result.missing)
        
        return ValidationResult(
            is_valid=len(missing_requirements) == 0,
            missing=missing_requirements
        )
    
    def _validate_fragment_requirements(self, user_id: int, fragment_id: int) -> ValidationResult:
        """
        Valida requisitos específicos del fragmento
        
        Args:
            user_id: ID del usuario
            fragment_id: ID del fragmento
            
        Returns:
            ValidationResult con resultado de validación
        """
        # TODO: Implementar validación específica del fragmento
        # Por ahora, simular validación exitosa
        return ValidationResult(is_valid=True)
    
    def _get_related_experiences(self, fragment_id: int) -> List[int]:
        """
        Obtiene experiencias relacionadas con un fragmento
        
        Args:
            fragment_id: ID del fragmento
            
        Returns:
            Lista de IDs de experiencias relacionadas
        """
        # TODO: Implementar consulta a base de datos
        # Por ahora, retornar lista vacía
        return []
    
    def _get_requirement_suggestions(self, missing_requirements: List[str]) -> List[str]:
        """
        Genera sugerencias para cumplir requisitos faltantes
        
        Args:
            missing_requirements: Lista de requisitos faltantes
            
        Returns:
            Lista de sugerencias
        """
        suggestions = []
        
        for req in missing_requirements:
            if 'vip' in req.lower():
                suggestions.append("Suscríbete al plan VIP para acceder a este contenido")
            elif 'level' in req.lower():
                suggestions.append("Completa más fragmentos para subir de nivel")
            elif 'item' in req.lower():
                suggestions.append("Compra el item requerido en la tienda")
            elif 'achievement' in req.lower():
                suggestions.append("Completa los logros requeridos")
        
        return suggestions
    
    def _track_conversion_opportunity(self, user_id: int, opportunity_type: str, 
                                    metadata: Dict[str, Any]) -> None:
        """
        Registra oportunidad de conversión para analytics
        
        Args:
            user_id: ID del usuario
            opportunity_type: Tipo de oportunidad
            metadata: Metadatos adicionales
        """
        self.event_bus.publish('analytics.conversion_opportunity', {
            'user_id': user_id,
            'opportunity_type': opportunity_type,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        })
    
    def _generate_personalized_vip_offer(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Genera oferta VIP personalizada para usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Dict con oferta personalizada o None
        """
        # TODO: Implementar lógica de generación de ofertas
        # Por ahora, retornar oferta básica
        return {
            'type': 'vip_subscription',
            'discount_percentage': 10,
            'trial_days': 7,
            'message': '¡Suscríbete ahora y obtén 7 días de prueba gratis!'
        }
    
    def _get_content_preview(self, fragment_id: int) -> str:
        """
        Obtiene vista previa del contenido VIP
        
        Args:
            fragment_id: ID del fragmento
            
        Returns:
            Texto de vista previa
        """
        # TODO: Implementar obtención de vista previa real
        return "Este es un fragmento exclusivo para miembros VIP. Suscríbete para acceder al contenido completo."
    
    def _register_default_validators(self) -> None:
        """Registra validadores por defecto"""
        self.validators['narrative'] = self._validate_narrative_requirements
        self.validators['vip'] = self._validate_vip_requirements
        self.validators['items'] = self._validate_item_requirements
        self.validators['level'] = self._validate_level_requirements
    
    def _validate_narrative_requirements(self, user_id: int, fragment_id: int) -> ValidationResult:
        """Valida requisitos narrativos"""
        # TODO: Implementar validación narrativa real
        return ValidationResult(is_valid=True)
    
    def _validate_vip_requirements(self, user_id: int, fragment_id: int) -> ValidationResult:
        """Valida requisitos VIP"""
        # TODO: Implementar validación VIP real
        return ValidationResult(is_valid=True)
    
    def _validate_item_requirements(self, user_id: int, fragment_id: int) -> ValidationResult:
        """Valida requisitos de items"""
        # TODO: Implementar validación de items real
        return ValidationResult(is_valid=True)
    
    def _validate_level_requirements(self, user_id: int, fragment_id: int) -> ValidationResult:
        """Valida requisitos de nivel"""
        # TODO: Implementar validación de nivel real
        return ValidationResult(is_valid=True)
    
    def REACCIONAR_CONTENIDO(self, user_id: int, content_type: str, content_id: int, reaction: str) -> Dict[str, Any]:
        """
        Procesa reacción de usuario con efectos multi-sistema
        
        Flujo:
        1. Validar que contenido existe
        2. Registrar reacción
        3. Otorgar besitos según configuración
        4. Actualizar estadísticas de engagement
        5. Verificar si desbloquea logros
        6. Actualizar progreso de misiones relacionadas
        
        Args:
            user_id: ID del usuario
            content_type: Tipo de contenido (narrative_fragment, channel_post, mission)
            content_id: ID del contenido
            reaction: Tipo de reacción (❤️, 🔥, ⭐, 👍)
            
        Returns:
            Dict con resultado de la operación
        """
        with self.transaction_manager.begin() as tx:
            # Validar contenido
            content = tx.execute(
                f'{content_type}.get_content',
                content_id=content_id
            )
            
            if not content:
                return {'success': False, 'reason': 'content_not_found'}
            
            # Registrar reacción
            tx.execute(
                'gamification.register_reaction',
                user_id=user_id,
                content_type=content_type,
                content_id=content_id,
                reaction=reaction
            )
            
            # Otorgar besitos
            besitos_config = self._get_reaction_rewards_config()
            besitos_amount = besitos_config.get(reaction, 0)
            
            if besitos_amount > 0:
                tx.execute(
                    'gamification.grant_besitos',
                    user_id=user_id,
                    amount=besitos_amount,
                    reason=f"Reacción {reaction} en {content_type}"
                )
            
            # Verificar logros
            achievements_unlocked = tx.execute(
                'gamification.check_reaction_achievements',
                user_id=user_id
            )
            
            # Actualizar misiones
            missions_progressed = tx.execute(
                'gamification.update_reaction_missions',
                user_id=user_id,
                reaction=reaction
            )
            
            # Emitir eventos
            tx.on_commit(lambda: self.event_bus.publish(
                'coordinator.content_reacted',
                {
                    'user_id': user_id,
                    'content_type': content_type,
                    'content_id': content_id,
                    'reaction': reaction,
                    'besitos_earned': besitos_amount,
                    'achievements': achievements_unlocked,
                    'missions': missions_progressed
                }
            ))
            
            return {
                'success': True,
                'besitos_earned': besitos_amount,
                'achievements_unlocked': achievements_unlocked,
                'missions_progressed': missions_progressed
            }
    
    def _get_reaction_rewards_config(self) -> Dict[str, int]:
        """
        Obtiene configuración de recompensas por reacción
        
        Returns:
            Dict con reacción -> cantidad de besitos
        """
        # Configuración por defecto
        return {
            '❤️': 10,  # love
            '🔥': 15,  # fire  
            '⭐': 20,  # star
            '👍': 5,   # like
        }


# Instancia global del CoordinadorCentral
coordinador_central = CoordinadorCentral(event_bus)