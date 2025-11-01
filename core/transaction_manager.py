"""
Transaction Manager para transacciones distribuidas en DianaBot

Este módulo gestiona transacciones que involucran múltiples sistemas
(narrativa, gamificación, administración, comercio) con capacidad
de rollback en caso de fallo.
"""

import logging
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TransactionError(Exception):
    """Excepción para errores en transacciones distribuidas"""
    pass


class OperationResult:
    """Resultado de una operación ejecutada en transacción"""
    
    def __init__(self, success: bool, data: Any = None, error: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error


class DistributedTransaction:
    """
    Transacción distribuida que coordina operaciones en múltiples sistemas
    """
    
    def __init__(self, manager: 'TransactionManager'):
        self.manager = manager
        self.operations: List[Dict[str, Any]] = []
        self.rollback_stack: List[Callable] = []
        self.commit_callbacks: List[Callable] = []
        self.started_at = datetime.now()
        
    def execute(self, operation_name: str, **kwargs) -> OperationResult:
        """
        Ejecuta una operación dentro de la transacción
        
        Args:
            operation_name: Nombre de la operación a ejecutar
            **kwargs: Parámetros de la operación
            
        Returns:
            OperationResult con el resultado de la operación
        """
        try:
            # Ejecutar operación
            result = self._execute_operation(operation_name, **kwargs)
            
            # Crear función de rollback
            rollback_func = self._create_rollback(operation_name, result, **kwargs)
            self.rollback_stack.append(rollback_func)
            
            # Registrar operación
            self.operations.append({
                'name': operation_name,
                'kwargs': kwargs,
                'result': result,
                'timestamp': datetime.now()
            })
            
            logger.info(f"Operación ejecutada en transacción: {operation_name}")
            return OperationResult(success=True, data=result)
            
        except Exception as e:
            logger.error(f"Error ejecutando operación {operation_name}: {e}")
            return OperationResult(success=False, error=str(e))
    
    def on_commit(self, callback: Callable) -> None:
        """
        Registra un callback a ejecutar después del commit exitoso
        
        Args:
            callback: Función a ejecutar después del commit
        """
        self.commit_callbacks.append(callback)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type is not None:
            # Hubo error: hacer rollback
            logger.warning(f"Transacción falló, ejecutando rollback: {exc_val}")
            self._rollback()
            return False
        else:
            # Todo bien: ejecutar callbacks
            self._commit()
            return True
    
    def _execute_operation(self, operation_name: str, **kwargs) -> Any:
        """
        Ejecuta una operación específica
        
        Args:
            operation_name: Nombre de la operación
            **kwargs: Parámetros
            
        Returns:
            Resultado de la operación
            
        Raises:
            TransactionError: Si la operación falla
        """
        # Mapeo de operaciones a funciones específicas
        operation_map = {
            # Operaciones de narrativa
            'narrative.apply_decision': self._narrative_apply_decision,
            'narrative.unlock_fragments': self._narrative_unlock_fragments,
            'narrative.get_fragment_content': self._narrative_get_fragment_content,
            
            # Operaciones de gamificación
            'gamification.grant_besitos': self._gamification_grant_besitos,
            'gamification.add_to_inventory': self._gamification_add_to_inventory,
            'gamification.progress_mission': self._gamification_progress_mission,
            
            # Operaciones de experiencias
            'experience.progress_component': self._experience_progress_component,
            
            # Operaciones de administración
            'admin.check_vip_membership': self._admin_check_vip_membership,
            'admin.verify_channel_membership': self._admin_verify_channel_membership,
            'admin.fix_channel_membership': self._admin_fix_channel_membership,
        }
        
        if operation_name not in operation_map:
            raise TransactionError(f"Operación no soportada: {operation_name}")
        
        return operation_map[operation_name](**kwargs)
    
    def _create_rollback(self, operation_name: str, result: Any, **kwargs) -> Callable:
        """
        Crea función de rollback para una operación
        
        Args:
            operation_name: Nombre de la operación
            result: Resultado de la operación
            **kwargs: Parámetros originales
            
        Returns:
            Función de rollback
        """
        # Mapeo de operaciones a funciones de rollback
        rollback_map = {
            'narrative.apply_decision': self._rollback_narrative_apply_decision,
            'narrative.unlock_fragments': self._rollback_narrative_unlock_fragments,
            'gamification.grant_besitos': self._rollback_gamification_grant_besitos,
            'gamification.add_to_inventory': self._rollback_gamification_add_to_inventory,
        }
        
        if operation_name in rollback_map:
            return lambda: rollback_map[operation_name](result, **kwargs)
        else:
            # Para operaciones sin rollback específico
            return lambda: None
    
    def _rollback(self) -> None:
        """Ejecuta rollback de todas las operaciones en orden inverso"""
        logger.info(f"Ejecutando rollback de {len(self.rollback_stack)} operaciones")
        
        for rollback_func in reversed(self.rollback_stack):
            try:
                rollback_func()
            except Exception as e:
                logger.error(f"Error en rollback: {e}")
    
    def _commit(self) -> None:
        """Ejecuta callbacks de commit"""
        logger.info(f"Ejecutando {len(self.commit_callbacks)} callbacks de commit")
        
        for callback in self.commit_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error en commit callback: {e}")
    
    # === IMPLEMENTACIONES DE OPERACIONES ===
    
    def _narrative_apply_decision(self, user_id: int, fragment_id: int, decision_id: int) -> Dict[str, Any]:
        """Aplica decisión narrativa"""
        # TODO: Integrar con módulo de narrativa existente
        logger.info(f"Aplicando decisión {decision_id} en fragmento {fragment_id} para usuario {user_id}")
        return {'success': True, 'rewards': {'besitos': 10}}
    
    def _narrative_unlock_fragments(self, user_id: int, fragment_ids: List[int]) -> Dict[str, Any]:
        """Desbloquea fragmentos narrativos"""
        # TODO: Integrar con módulo de narrativa existente
        logger.info(f"Desbloqueando fragmentos {fragment_ids} para usuario {user_id}")
        return {'success': True, 'unlocked': fragment_ids}
    
    def _narrative_get_fragment_content(self, user_id: int, fragment_id: int) -> Dict[str, Any]:
        """Obtiene contenido de fragmento"""
        # TODO: Integrar con módulo de narrativa existente
        logger.info(f"Obteniendo contenido de fragmento {fragment_id} para usuario {user_id}")
        return {'content': 'Contenido del fragmento', 'is_vip': False}
    
    def _gamification_grant_besitos(self, user_id: int, amount: int, reason: str) -> Dict[str, Any]:
        """Otorga besitos a usuario"""
        # TODO: Integrar con módulo de gamificación existente
        logger.info(f"Otorgando {amount} besitos a usuario {user_id}: {reason}")
        return {'success': True, 'new_balance': 100 + amount}
    
    def _gamification_add_to_inventory(self, user_id: int, item_id: int) -> Dict[str, Any]:
        """Agrega item al inventario"""
        # TODO: Integrar con módulo de gamificación existente
        logger.info(f"Agregando item {item_id} al inventario de usuario {user_id}")
        return {'success': True, 'item_added': item_id}
    
    def _gamification_progress_mission(self, user_id: int, mission_id: int, progress_data: Dict) -> Dict[str, Any]:
        """Actualiza progreso de misión"""
        # TODO: Integrar con módulo de gamificación existente
        logger.info(f"Actualizando progreso de misión {mission_id} para usuario {user_id}")
        return {'success': True, 'mission_progress': progress_data}
    
    def _experience_progress_component(self, user_id: int, experience_id: int, 
                                     component_type: str, component_id: int) -> Dict[str, Any]:
        """Actualiza progreso de componente de experiencia"""
        # TODO: Integrar con módulo de experiencias
        logger.info(f"Actualizando progreso de experiencia {experience_id} para usuario {user_id}")
        return {'success': True, 'component_completed': component_id}
    
    def _admin_check_vip_membership(self, user_id: int) -> bool:
        """Verifica membresía VIP"""
        # TODO: Integrar con módulo de administración existente
        logger.info(f"Verificando membresía VIP para usuario {user_id}")
        return True  # Simulado
    
    def _admin_verify_channel_membership(self, user_id: int, channel_type: str) -> bool:
        """Verifica membresía de canal"""
        # TODO: Integrar con módulo de administración existente
        logger.info(f"Verificando membresía de canal {channel_type} para usuario {user_id}")
        return True  # Simulado
    
    def _admin_fix_channel_membership(self, user_id: int) -> None:
        """Corrige membresía de canal"""
        # TODO: Integrar con módulo de administración existente
        logger.info(f"Corrigiendo membresía de canal para usuario {user_id}")
    
    # === IMPLEMENTACIONES DE ROLLBACK ===
    
    def _rollback_narrative_apply_decision(self, result: Dict, user_id: int, fragment_id: int, decision_id: int) -> None:
        """Rollback de aplicación de decisión narrativa"""
        logger.info(f"Rollback de decisión {decision_id} en fragmento {fragment_id}")
        # TODO: Implementar rollback específico
    
    def _rollback_narrative_unlock_fragments(self, result: Dict, user_id: int, fragment_ids: List[int]) -> None:
        """Rollback de desbloqueo de fragmentos"""
        logger.info(f"Rollback de desbloqueo de fragmentos {fragment_ids}")
        # TODO: Implementar rollback específico
    
    def _rollback_gamification_grant_besitos(self, result: Dict, user_id: int, amount: int, reason: str) -> None:
        """Rollback de otorgamiento de besitos"""
        logger.info(f"Rollback de {amount} besitos otorgados a usuario {user_id}")
        # TODO: Implementar rollback específico
    
    def _rollback_gamification_add_to_inventory(self, result: Dict, user_id: int, item_id: int) -> None:
        """Rollback de adición al inventario"""
        logger.info(f"Rollback de item {item_id} agregado al inventario de usuario {user_id}")
        # TODO: Implementar rollback específico


class TransactionManager:
    """
    Gestor de transacciones distribuidas para coordinación multi-módulo
    """
    
    def __init__(self):
        self.active_transactions: List[DistributedTransaction] = []
    
    def begin(self) -> DistributedTransaction:
        """
        Inicia una nueva transacción distribuida
        
        Returns:
            DistributedTransaction para ejecutar operaciones
        """
        transaction = DistributedTransaction(self)
        self.active_transactions.append(transaction)
        logger.info("Nueva transacción distribuida iniciada")
        return transaction
    
    def get_active_transactions_count(self) -> int:
        """Obtiene número de transacciones activas"""
        return len(self.active_transactions)


# Instancia global del TransactionManager
transaction_manager = TransactionManager()