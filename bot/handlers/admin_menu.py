"""
Gestor de Estado de Menús Administrativos - DianaBot

Maneja el estado de navegación en los menús administrativos
para permitir flujos multi-paso y navegación entre menús.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AdminMenuStateManager:
    """
    Gestiona el estado de navegación en menús administrativos
    Permite flujos multi-paso para operaciones complejas
    """
    
    def __init__(self):
        # Estructura: {user_id: {"current_menu": "menu_name", "data": {...}, "step": 1}}
        self.user_states: Dict[int, Dict[str, Any]] = {}
        
        # Tiempo de expiración de estados (en segundos)
        self.state_timeout = 3600  # 1 hora
    
    def set_user_state(self, user_id: int, menu: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Establece el estado actual del usuario en un menú específico
        
        Args:
            user_id: ID del usuario administrador
            menu: Nombre del menú actual
            data: Datos adicionales del estado
        """
        self.user_states[user_id] = {
            "current_menu": menu,
            "data": data or {},
            "step": 1,
            "timestamp": datetime.now().timestamp()
        }
        logger.debug(f"Estado establecido para usuario {user_id}: {menu}")
    
    def get_user_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene el estado actual del usuario
        
        Args:
            user_id: ID del usuario administrador
            
        Returns:
            Dict con el estado del usuario o None si no existe
        """
        state = self.user_states.get(user_id)
        
        # Verificar expiración
        if state and self._is_state_expired(state):
            self.clear_user_state(user_id)
            return None
            
        return state
    
    def update_user_state(self, user_id: int, updates: Dict[str, Any]) -> None:
        """
        Actualiza el estado del usuario con nuevos datos
        
        Args:
            user_id: ID del usuario administrador
            updates: Diccionario con campos a actualizar
        """
        if user_id in self.user_states:
            self.user_states[user_id].update(updates)
            self.user_states[user_id]["timestamp"] = datetime.now().timestamp()
            logger.debug(f"Estado actualizado para usuario {user_id}: {updates}")
    
    def clear_user_state(self, user_id: int) -> None:
        """
        Limpia el estado del usuario
        
        Args:
            user_id: ID del usuario administrador
        """
        if user_id in self.user_states:
            del self.user_states[user_id]
            logger.debug(f"Estado limpiado para usuario {user_id}")
    
    def set_step(self, user_id: int, step: int) -> None:
        """
        Establece el paso actual en un flujo multi-paso
        
        Args:
            user_id: ID del usuario administrador
            step: Número del paso actual
        """
        self.update_user_state(user_id, {"step": step})
    
    def get_step(self, user_id: int) -> int:
        """
        Obtiene el paso actual del usuario
        
        Args:
            user_id: ID del usuario administrador
            
        Returns:
            Número del paso actual (1 por defecto)
        """
        state = self.get_user_state(user_id)
        return state.get("step", 1) if state else 1
    
    def set_data(self, user_id: int, key: str, value: Any) -> None:
        """
        Establece un dato específico en el estado del usuario
        
        Args:
            user_id: ID del usuario administrador
            key: Clave del dato
            value: Valor del dato
        """
        state = self.get_user_state(user_id)
        if state:
            state["data"][key] = value
            self.update_user_state(user_id, {"data": state["data"]})
    
    def get_data(self, user_id: int, key: str, default: Any = None) -> Any:
        """
        Obtiene un dato específico del estado del usuario
        
        Args:
            user_id: ID del usuario administrador
            key: Clave del dato
            default: Valor por defecto si no existe
            
        Returns:
            Valor del dato o el valor por defecto
        """
        state = self.get_user_state(user_id)
        if state and "data" in state:
            return state["data"].get(key, default)
        return default
    
    def get_current_menu(self, user_id: int) -> Optional[str]:
        """
        Obtiene el menú actual del usuario
        
        Args:
            user_id: ID del usuario administrador
            
        Returns:
            Nombre del menú actual o None
        """
        state = self.get_user_state(user_id)
        return state.get("current_menu") if state else None
    
    def _is_state_expired(self, state: Dict[str, Any]) -> bool:
        """
        Verifica si un estado ha expirado
        
        Args:
            state: Estado del usuario
            
        Returns:
            True si el estado ha expirado
        """
        timestamp = state.get("timestamp", 0)
        current_time = datetime.now().timestamp()
        return (current_time - timestamp) > self.state_timeout
    
    def cleanup_expired_states(self) -> None:
        """Limpia todos los estados expirados"""
        current_time = datetime.now().timestamp()
        expired_users = []
        
        for user_id, state in self.user_states.items():
            if self._is_state_expired(state):
                expired_users.append(user_id)
        
        for user_id in expired_users:
            self.clear_user_state(user_id)
        
        if expired_users:
            logger.info(f"Limpieza de estados expirados: {len(expired_users)} usuarios")


# Instancia global del gestor de estado de menús
menu_state_manager = AdminMenuStateManager()