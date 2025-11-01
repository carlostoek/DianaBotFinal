"""
Tests unitarios simples para el CoordinadorCentral y TransactionManager
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

from unittest.mock import Mock, patch


class TestTransactionManagerSimple:
    """Tests simples para TransactionManager"""
    
    def test_transaction_manager_basic(self):
        """Test básico de TransactionManager"""
        # Importar aquí para evitar problemas de importación
        from core.transaction_manager import TransactionManager, DistributedTransaction
        
        manager = TransactionManager()
        assert manager.active_transactions == []
        assert manager.get_active_transactions_count() == 0
        
        # Test que se puede iniciar una transacción
        transaction = manager.begin()
        assert isinstance(transaction, DistributedTransaction)
        assert manager.get_active_transactions_count() == 1
    
    def test_distributed_transaction_basic(self):
        """Test básico de DistributedTransaction"""
        from core.transaction_manager import TransactionManager
        
        manager = TransactionManager()
        
        # Test que funciona como context manager
        with manager.begin() as tx:
            assert tx.operations == []
            assert tx.rollback_stack == []
            assert tx.commit_callbacks == []
    
    def test_operation_result(self):
        """Test de OperationResult"""
        from core.transaction_manager import OperationResult
        
        # Test resultado exitoso
        result1 = OperationResult(success=True, data={'test': 'data'})
        assert result1.success is True
        assert result1.data == {'test': 'data'}
        assert result1.error is None
        
        # Test resultado fallido
        result2 = OperationResult(success=False, error='Test error')
        assert result2.success is False
        assert result2.error == 'Test error'
        assert result2.data is None


class TestCoordinadorCentralSimple:
    """Tests simples para CoordinadorCentral"""
    
    def test_validation_result(self):
        """Test de ValidationResult"""
        from core.coordinator import ValidationResult
        
        # Test con validación exitosa
        result1 = ValidationResult(is_valid=True)
        assert result1.is_valid is True
        assert result1.missing == []
        assert result1.suggestions == []
        
        # Test con validación fallida
        result2 = ValidationResult(
            is_valid=False, 
            missing=['vip_required', 'level_5'],
            suggestions=['Suscríbete al VIP', 'Sube de nivel']
        )
        assert result2.is_valid is False
        assert 'vip_required' in result2.missing
        assert 'Suscríbete al VIP' in result2.suggestions
    
    @patch('core.coordinator.event_bus')
    def test_coordinator_initialization(self, mock_event_bus):
        """Test que CoordinadorCentral se inicializa correctamente"""
        from core.coordinator import CoordinadorCentral
        
        coordinator = CoordinadorCentral(mock_event_bus)
        
        assert coordinator.event_bus == mock_event_bus
        assert 'narrative' in coordinator.validators
        assert 'vip' in coordinator.validators
        assert 'items' in coordinator.validators
        assert 'level' in coordinator.validators
    
    def test_get_requirement_suggestions(self):
        """Test que se generan sugerencias correctamente"""
        from core.coordinator import CoordinadorCentral
        
        coordinator = CoordinadorCentral(Mock())
        
        missing_requirements = [
            'vip_required',
            'min_level_5',
            'item_sword_required',
            'achievement_explorer'
        ]
        
        suggestions = coordinator._get_requirement_suggestions(missing_requirements)
        
        assert len(suggestions) == 4
        assert any('VIP' in s for s in suggestions)
        assert any('nivel' in s for s in suggestions)
        assert any('tienda' in s for s in suggestions)
        assert any('logros' in s for s in suggestions)
    
    def test_generate_personalized_vip_offer(self):
        """Test que se genera oferta VIP"""
        from core.coordinator import CoordinadorCentral
        
        coordinator = CoordinadorCentral(Mock())
        
        offer = coordinator._generate_personalized_vip_offer(user_id=1)
        
        assert offer is not None
        assert offer['type'] == 'vip_subscription'
        assert 'discount_percentage' in offer
        assert 'trial_days' in offer
        assert 'message' in offer
    
    def test_get_content_preview(self):
        """Test que se obtiene vista previa de contenido"""
        from core.coordinator import CoordinadorCentral
        
        coordinator = CoordinadorCentral(Mock())
        
        preview = coordinator._get_content_preview(fragment_id=1)
        
        assert isinstance(preview, str)
        assert 'VIP' in preview
        assert 'exclusivo' in preview


if __name__ == '__main__':
    # Ejecutar tests simples
    import unittest
    
    # Crear test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTransactionManagerSimple))
    suite.addTest(unittest.makeSuite(TestCoordinadorCentralSimple))
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\nTests ejecutados: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")